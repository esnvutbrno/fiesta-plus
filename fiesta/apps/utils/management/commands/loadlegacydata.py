from __future__ import annotations

import itertools
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import djclick as click
import requests
from allauth.account.models import EmailAddress
from click import secho
from django.core.files.images import ImageFile
from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware
from django_countries.fields import Country
from phonenumber_field.phonenumber import to_python

from apps.accounts.forms.social_accounts_fields import clean_facebook, clean_instagram
from apps.accounts.hashers import LegacyBCryptSHA256PasswordHasher
from apps.accounts.models import User, UserProfile
from apps.accounts.services.user_profile_state_synchronizer import synchronizer
from apps.buddy_system.apps import BuddySystemConfig
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
from apps.fiestarequests.matching_policy import ManualByEditorMatchingPolicy, ManualByMemberMatchingPolicy
from apps.pickup_system.apps import PickupSystemConfig
from apps.pickup_system.models import PickupRequest, PickupRequestMatch, PickupSystemConfiguration
from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.sections.models import Section, SectionMembership, SectionUniversity
from apps.sections.models.services.section_plugins_reconciler import SectionPluginsReconciler
from apps.universities.models import Faculty, University

LOAD_MEMBERS = """
SELECT
    du.user_id, u.password,
    du.name, du.surname,
    du.registered,
    du.gender,
    du.facebook_url,
    du.instagram_url,
    du.phone_number,
    du.birthday,
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
-- where data_user = 'deawer23@seznam.cz'
-- WHERE ra.role IN ('member', 'admin', 'editor')
-- where du.registered > '2023-09-01'
GROUP BY du.user_id
ORDER BY u.user_id;
"""

LOAD_BUDDY_REQUESTS = """
SELECT
    br.data_user,
    br.description,
    issuer_u.university,
    issuer.faculty_id,
    matcher_u.university,
    matcher.faculty_id,
    bm.member,
    bm.created
FROM buddy_request br
INNER JOIN data_user issuer on br.data_user = issuer.user_id
INNER JOIN user issuer_u on br.data_user = issuer_u.user_id
LEFT JOIN buddy_match bm ON bm.international = br.data_user
LEFT JOIN data_user matcher ON bm.member = matcher.user_id
LEFT JOIN user matcher_u ON bm.member = matcher_u.user_id
-- where issuer.registered > '2023-09-01'
;
"""

LOAD_PICKUP_REQUESTS = """
SELECT
    pr.data_user,
    pr.description,
    pr.date_arrival,
    pr.place_arrival,
    issuer_u.university,
    issuer.faculty_id,
    matcher_u.university,
    matcher.faculty_id,
    pm.member,
    pm.created
FROM pickup_request pr
INNER JOIN data_user issuer on pr.data_user = issuer.user_id
INNER JOIN user issuer_u on pr.data_user = issuer_u.user_id
LEFT JOIN pickup_match pm ON pm.international = pr.data_user
LEFT JOIN data_user matcher ON pm.member = matcher.user_id
LEFT JOIN user matcher_u ON pm.member = matcher_u.user_id
-- where issuer.registered > '2023-09-01'
;
"""

LOAD_FACULTIES = """
select
    faculty.id, -- id
    faculty.faculty_shortcut, -- FIT
    faculty.university_id, -- BUT
faculty.faculty -- faculty of
from faculty
inner join fiesta.university u on faculty.university_id = u.id
"""

LOAD_BUDDY_SETTINGS = """
select
    u.section_short,
       show_manual,
       show_image,
       show_university,
       show_state,
       show_faculty,
       show_gender,
       `limit`
from buddy_settings
inner join university u on buddy_settings.university_id = u.id
inner join module_assignment ma on u.id = ma.university
where ma.module = 'BuddyManagement'
;
"""

LOAD_PICKUP_SETTINGS = """
select
    u.section_short,
       show_image,
       show_university,
       show_state,
       show_faculty,
       show_gender
from pickup_settings
inner join university u on pickup_settings.university_id = u.id
inner join module_assignment ma on u.id = ma.university
where ma.module = 'PickupManagement'
;
"""

ID_TO_USER: dict[str, User] = {}
ID_TO_FACULTY: dict[str, Faculty] = {}

WORKER_POOL = ProcessPoolExecutor()


def load_faculties(*, cursor: CursorWrapper):
    cursor.execute(LOAD_FACULTIES)

    for f_id, f_abbr, uni_abbr, f_name in cursor.fetchall():
        u, _ = University.objects.get_or_create(
            abbr=uni_abbr,
            defaults=dict(name=uni_abbr),
        )
        f, _ = Faculty.objects.update_or_create(
            abbr=f_abbr,
            university=u,
            defaults=dict(name=f_name),
        )
        ID_TO_FACULTY[f_id] = f
        secho(f"Processed faculty {f_abbr}.")


def unknown_faculty_for_university(uni_abbr: str):
    return Faculty.objects.get_or_create(
        abbr="UND",
        university=University.objects.get(abbr=uni_abbr),
        defaults=dict(name="Unknown"),
    )[0]


def load_pickup_requests(*, cursor: CursorWrapper):
    secho("Loading pickup requests.")
    cursor.execute(LOAD_PICKUP_REQUESTS)
    for i, row in enumerate(cursor.fetchall(), start=1):
        (
            issuer_email,
            description,
            date_arrival,
            place_arrival,
            issuer_university,
            issuer_faculty,
            matcher_university,
            matcher_faculty,
            matched_by_email,
            matched_at,
        ) = row

        secho(f"Processing {i: >4} {row=}.")

        if issuer_faculty:
            issuer_f = ID_TO_FACULTY[issuer_faculty]
        else:
            issuer_f = unknown_faculty_for_university(issuer_university)

        responsible_section = Section.objects.filter(universities__abbr=issuer_university).first()

        pr, _ = PickupRequest.objects.update_or_create(
            issuer=ID_TO_USER[issuer_email],
            responsible_section=responsible_section,
            defaults=dict(
                note=description,
                state=PickupRequest.State.MATCHED if matched_by_email else PickupRequest.State.CREATED,
                issuer_faculty=issuer_f,
                created=ID_TO_USER[issuer_email].date_joined,
                time=make_aware(date_arrival),
                place=place_arrival,
                location=None,
            ),
        )

        if matched_by_email:
            if matcher_faculty:
                matcher_f = ID_TO_FACULTY.get(matcher_faculty)
            else:
                matcher_f = unknown_faculty_for_university(matcher_university)

            PickupRequestMatch.objects.update_or_create(
                request=pr,
                defaults=dict(
                    matcher=ID_TO_USER[matched_by_email],
                    created=make_aware(matched_at) if matched_at else ID_TO_USER[matched_by_email].modified,
                    matcher_faculty=matcher_f,
                ),
            )


def load_buddy_requests(*, cursor: CursorWrapper):
    secho("Loading buddy requests.")
    cursor.execute(LOAD_BUDDY_REQUESTS)
    for i, row in enumerate(cursor.fetchall(), start=1):
        (
            issuer_email,
            description,
            issuer_university,
            issuer_faculty,
            matcher_university,
            matcher_faculty,
            matched_by_email,
            matched_at,
        ) = row

        secho(f"Processing {i: >4} {row=}.")

        if issuer_faculty:
            issuer_f = ID_TO_FACULTY[issuer_faculty]
        else:
            issuer_f = unknown_faculty_for_university(issuer_university)

        responsible_section = Section.objects.filter(universities__abbr=issuer_university).first()

        br, _ = BuddyRequest.objects.update_or_create(
            issuer=ID_TO_USER[issuer_email],
            responsible_section=responsible_section,
            defaults=dict(
                note=description,
                state=BuddyRequest.State.MATCHED if matched_by_email else BuddyRequest.State.CREATED,
                issuer_faculty=issuer_f,
                created=ID_TO_USER[issuer_email].date_joined,
            ),
        )

        if matched_by_email:
            if matcher_faculty:
                matcher_f = ID_TO_FACULTY.get(matcher_faculty)
            else:
                matcher_f = unknown_faculty_for_university(matcher_university)

            BuddyRequestMatch.objects.update_or_create(
                request=br,
                defaults=dict(
                    matcher=ID_TO_USER[matched_by_email],
                    created=make_aware(matched_at) if matched_at else None,
                    matcher_faculty=matcher_f,
                ),
            )


def load_users(*, cursor: CursorWrapper):
    cursor.execute(LOAD_MEMBERS)

    # for email, user in WORKER_POOL.map(process_user_row, cursor.fetchall(), itertools.count(1)):
    for email, user in map(process_user_row, cursor.fetchall(), itertools.count(1)):
        ID_TO_USER[email] = user


def load_buddy_settings(*, cursor: CursorWrapper):
    cursor.execute(LOAD_BUDDY_SETTINGS)

    for (
        section_short,
        matched_by_editors,
        show_image,
        show_university,
        show_state,
        show_faculty,
        show_gender,
        limit,
    ) in cursor.fetchall():
        section = Section.objects.get(name=section_short)

        conf, _ = BuddySystemConfiguration.objects.select_for_update().update_or_create(
            section=section,
            defaults=dict(
                shared=False,
                matching_policy=(
                    ManualByMemberMatchingPolicy.id,
                    ManualByEditorMatchingPolicy.id,
                )[matched_by_editors],
                display_issuer_first_name=False,
                display_issuer_last_name=False,
                display_issuer_picture=show_image,
                display_issuer_gender=show_gender,
                display_issuer_country=show_state,
                display_issuer_university=show_university,
                display_issuer_faculty=show_faculty,
                rolling_limit=limit,
                enable_note_from_matcher=True,
            ),
        )
        plugin, _ = Plugin.objects.get_or_create(
            section=section,
            app_label=all_plugins_mapped_to_class().get(BuddySystemConfig).label,
            defaults=dict(
                state=Plugin.State.ENABLED,
                configuration=conf,
            ),
        )
        secho(f"Processed {section_short} into {plugin=} with {conf=}.")


def load_pickup_settings(*, cursor: CursorWrapper):
    cursor.execute(LOAD_PICKUP_SETTINGS)

    for (
        section_short,
        show_image,
        show_university,
        show_state,
        show_faculty,
        show_gender,
    ) in cursor.fetchall():
        section = Section.objects.get(name=section_short)

        conf, _ = PickupSystemConfiguration.objects.select_for_update().update_or_create(
            section=section,
            defaults=dict(
                shared=False,
                # matching_policy=(
                #     ManualByMemberMatchingPolicy.id,
                #     ManualByEditorMatchingPolicy.id,
                # )[matched_by_editors],
                display_issuer_first_name=False,
                display_issuer_last_name=False,
                display_issuer_picture=show_image,
                display_issuer_gender=show_gender,
                display_issuer_country=show_state,
                display_issuer_university=show_university,
                display_issuer_faculty=show_faculty,
                rolling_limit=0,
                enable_note_from_matcher=True,
            ),
        )
        plugin, _ = Plugin.objects.get_or_create(
            section=section,
            app_label=all_plugins_mapped_to_class().get(PickupSystemConfig).label,
            defaults=dict(
                state=Plugin.State.ENABLED,
                configuration=conf,
            ),
        )
        secho(f"Processed {section_short} into {plugin=} with {conf=}.")


def process_user_row(row, i):
    (
        email,
        password,
        first_name,
        last_name,
        registered,
        gender,
        facebook_url,
        instagram_url,
        phone_number,
        birthday,
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
    # return email, get_single_object_or_none(User, username=email)

    # password = password.split('$')[3]
    # is:        $2y$10$t9haqcKqlgXKrCv1pVTAxuqKh7vDtwksh0w7PXb44eNjRQOvY58Mu
    # wanted: alg$2y$10$iqdxi8RXWCADYYFsfyHD1u6rrXBW4v73.AGHZ32uUYu9gVjD0x7IG
    user, created = User.objects.select_for_update().update_or_create(
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
    EmailAddress.objects.select_for_update().update_or_create(
        email=email,
        defaults=dict(
            user=user,
            verified=True,
            primary=True,
        ),
    )
    ID_TO_USER[email] = user

    # if not created:
    #     continue

    section, _ = Section.objects.select_for_update().update_or_create(
        name=section_short,
        defaults=dict(
            space_slug=slugify(section_short.replace(" ", "")),
            country=Country("CZ"),
        ),
    )
    SectionMembership.objects.select_for_update().update_or_create(
        section=section,
        user=user,
        defaults=dict(
            created=make_aware(registered) if registered else timezone.now(),
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
        ),
    )
    university, _ = University.objects.get_or_create(abbr=uni_id, defaults=dict(name=uni_name, country=Country("CZ")))
    SectionUniversity.objects.select_for_update().update_or_create(
        section=section,
        university=university,
    )
    faculty = None
    if faculty_name:
        faculty, _ = Faculty.objects.select_for_update().update_or_create(
            university=university,
            abbr=faculty_short,
            defaults=dict(name=faculty_name),
        )

    # is_international = highest_role == SectionMembership.Role.INTERNATIONAL
    user_profile, _ = UserProfile.objects.select_for_update().update_or_create(
        user=user,
        defaults=dict(
            nationality=Country(country_code),
            university=university if not faculty else None,
            faculty=faculty,
            gender={
                "f": UserProfile.Gender.FEMALE,
                "m": UserProfile.Gender.MALE,
            }[gender],
            facebook=clean_facebook(facebook_url) or "",
            instagram=clean_instagram(instagram_url) or "",
            phone_number=to_python(phone_number) or "",
            birth_date=birthday,
            avatar_slug=avatar_name,
        ),
    )
    return email, user

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

    return email, user


def fill_id_to_user():
    for user in User.objects.all():
        ID_TO_USER[user.username] = user


def reconcile_sections():
    for s in Section.objects.all():
        SectionPluginsReconciler.reconcile(s)
        secho(f"Reconciled section {s}.")


def load(cursor: CursorWrapper):
    load_faculties(cursor=cursor)

    load_users(cursor=cursor)
    # fill_id_to_user()
    load_buddy_requests(cursor=cursor)
    load_pickup_requests(cursor=cursor)

    load_buddy_settings(cursor=cursor)
    load_pickup_settings(cursor=cursor)


@click.command()
def load_legacy_data():
    with connections["legacydb"].cursor() as cursor, synchronizer.without_profile_revalidation():
        load(cursor=cursor)
