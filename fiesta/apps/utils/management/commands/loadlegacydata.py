from __future__ import annotations

import itertools
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import djclick as click
import requests
from click import secho
from django.core.files.images import ImageFile
from django.db import connections, transaction
from django.db.backends.utils import CursorWrapper
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware
from django_countries.fields import Country

from apps.accounts.hashers import LegacyBCryptSHA256PasswordHasher
from apps.accounts.models import User, UserProfile
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.sections.models import Section, SectionMembership, SectionUniversity
from apps.universities.models import Faculty, University

LOAD_MEMBERS = """
SELECT
    du.user_id, u.password,
    du.name, du.surname,
    du.registered,
    u.status,
    u.signature,
    json_array(ra.role),
    uni.section_short,
    f.faculty, f.faculty_shortcut,
    c.code_id, uni.id, uni.name
FROM data_user du
INNER JOIN user u ON du.user_id = u.user_id
INNER JOIN university uni ON uni.id = u.university
INNER JOIN role_assignment ra ON ra.data_user = du.user_id
LEFT JOIN country c on du.country_id = c.code_id
LEFT JOIN faculty f on du.faculty_id = f.id
-- WHERE ra.role IN ('member', 'admin', 'editor')
GROUP BY du.user_id
ORDER BY u.user_id;
"""

LOAD_BUDDY_REQUESTS = """
SELECT
    br.data_user,
    br.description,
    u.university,
    bm.member,
    bm.created
FROM buddy_request br
INNER JOIN user u on br.data_user = u.user_id
LEFT JOIN buddy_match bm ON bm.international = br.data_user
"""

ID_TO_USER = {}

WORKER_POOL = ProcessPoolExecutor()


def load_requests(*, cursor: CursorWrapper):
    cursor.execute(LOAD_BUDDY_REQUESTS)
    for i, row in enumerate(cursor.fetchall(), start=1):
        (
            issuer_email,
            description,
            issuer_university,
            matched_by_email,
            matched_at,
        ) = row

        responsible_section = Section.objects.filter(universities__abbr=issuer_university).first()

        br, _ = BuddyRequest.objects.update_or_create(
            issuer=ID_TO_USER[issuer_email],
            responsible_section=responsible_section,
            defaults=dict(
                note=description,
                state=BuddyRequest.State.MATCHED if matched_by_email else BuddyRequest.State.CREATED,
            ),
        )

        if matched_by_email:
            BuddyRequestMatch.objects.create_or_update(
                request=br,
                defaults=dict(
                    matcher=ID_TO_USER[matched_by_email],
                    created=make_aware(matched_at) if matched_at else None,
                ),
            )

        secho("Processing {i: >4}: {desc}.".format(i=i, desc=description[:32].replace("\n", " ")))


def load_users(*, cursor: CursorWrapper):
    cursor.execute(LOAD_MEMBERS)

    for email, user in WORKER_POOL.map(process_user_row, cursor.fetchall(), itertools.count(1)):
        ID_TO_USER[email] = user


def process_user_row(row, i):
    (
        email,
        password,
        first_name,
        last_name,
        registered,
        status,
        avatar_name,
        roles,
        section_short,
        faculty_name,
        faculty_short,
        country_code,
        uni_id,
        uni_name,
    ) = row

    secho(f"Processing {i: >4}: {email}.")
    # password = password.split('$')[3]
    # is:        $2y$10$t9haqcKqlgXKrCv1pVTAxuqKh7vDtwksh0w7PXb44eNjRQOvY58Mu
    # wanted: alg$2y$10$iqdxi8RXWCADYYFsfyHD1u6rrXBW4v73.AGHZ32uUYu9gVjD0x7IG
    user, created = User.objects.update_or_create(
        username=email,
        defaults=dict(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=f"{LegacyBCryptSHA256PasswordHasher.algorithm}${password}",
            date_joined=make_aware(registered) if registered else timezone.now(),
            state={
                "active": User.State.ACTIVE,
                "pending": User.State.REGISTERED,
                "uncompleted": User.State.REGISTERED,
                "enabled": User.State.EXPIRED,
                "banned": User.State.BANNED,
            }[status],
        ),
    )
    ID_TO_USER[email] = user

    # if not created:
    #     continue

    section, _ = Section.objects.update_or_create(
        name=section_short,
        defaults=dict(
            country=Country("CZ"),
            space_slug=slugify(section_short.replace(" ", "")),
        ),
    )
    SectionMembership.objects.update_or_create(
        section=section,
        user=user,
        role=(
            SectionMembership.Role.ADMIN
            if "admin" in roles
            else (
                SectionMembership.Role.EDITOR
                if "editor" in roles
                else (SectionMembership.Role.MEMBER if "member" in roles else SectionMembership.Role.INTERNATIONAL)
            )
        ),
        # TODO: state
        state=SectionMembership.State.ACTIVE,
        defaults=dict(created=make_aware(registered) if registered else timezone.now()),
    )
    university, _ = University.objects.update_or_create(
        abbr=uni_id, defaults=dict(name=uni_name, country=Country("CZ"))
    )
    SectionUniversity.objects.update_or_create(
        section=section,
        university=university,
    )
    faculty = None
    if faculty_name:
        faculty, _ = Faculty.objects.update_or_create(
            university=university,
            abbr=faculty_short,
            defaults=dict(name=faculty_name),
        )

    # is_international = highest_role == SectionMembership.Role.INTERNATIONAL
    user_profile, _ = UserProfile.objects.update_or_create(
        user=user,
        defaults=dict(
            nationality=Country(country_code),
            university=university if not faculty else None,
            faculty=faculty,
        ),
    )

    if avatar_name and not user_profile.picture:
        r = requests.get(f"https://fiesta.esncz.org/images/avatar/{avatar_name}.jpg")
        user_profile.picture = (
            ImageFile(
                BytesIO(r.content),
                name="image.jpg",
            )
            if r.status_code == 200
            else None
        )
        user_profile.save(update_fields=["picture"])

    return (email, user)


def load(cursor: CursorWrapper):
    with transaction.atomic(using="legacydb"):
        load_users(cursor=cursor)
        load_requests(cursor=cursor)


@click.command()
def load_legacy_data():
    with connections["legacydb"].cursor() as cursor:
        load(cursor=cursor)
