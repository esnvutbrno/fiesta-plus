import djclick as click

from click import secho
from django.db import connections, transaction
from django.db.backends.utils import CursorWrapper
from django.utils import timezone
from django.utils.timezone import make_aware
from django_countries.fields import Country

from apps.accounts.hashers import LegacyBCryptSHA256PasswordHasher
from apps.accounts.models import User, UserProfile
from apps.sections.models import Section, SectionMembership, SectionUniversity
from apps.universities.models import Faculty, University

LOAD_MEMBERS = """
SELECT
    du.user_id, u.password,
    du.name, du.surname,
    du.registered,
    u.status,
    json_array(ra.role),
    uni.section_short,
    f.faculty, f.faculty_shortcut,
    c.code_id, uni.id, uni.name
FROM data_user du
INNER JOIN user u ON du.user_id = u.user_id
INNER JOIN university uni ON uni.id = u.university
INNER JOIN role_assignment ra ON ra.data_user = du.user_id
INNER JOIN country c on du.country_id = c.code_id
LEFT JOIN faculty f on du.faculty_id = f.id
WHERE ra.role IN ('member', 'admin', 'editor')
GROUP BY du.user_id
ORDER BY u.user_id;
"""


def load_users(*, cursor: CursorWrapper):
    cursor.execute(LOAD_MEMBERS)
    for i, row in enumerate(cursor.fetchall(), start=1):
        (
            email,
            password,
            first_name,
            last_name,
            registered,
            status,
            roles,
            section_short,
            faculty_name,
            faculty_short,
            country_code,
            uni_id,
            uni_name,
        ) = row
        # password = password.split('$')[3]
        # is:        $2y$10$t9haqcKqlgXKrCv1pVTAxuqKh7vDtwksh0w7PXb44eNjRQOvY58Mu
        # wanted: alg$2y$10$iqdxi8RXWCADYYFsfyHD1u6rrXBW4v73.AGHZ32uUYu9gVjD0x7IG
        user, _ = User.objects.update_or_create(
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
        section, _ = Section.objects.update_or_create(
            name=section_short,
            defaults=dict(
                country=Country("CZ"),
            ),
        )
        SectionMembership.objects.update_or_create(
            section=section,
            user=user,
            role=SectionMembership.Role.ADMIN
            if "admin" in roles
            else (
                SectionMembership.Role.EDITOR
                if "editor" in roles
                else (SectionMembership.Role.MEMBER)
            ),
            # TODO: state
            state=SectionMembership.State.ACTIVE,
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
        user_profile, _ = UserProfile.objects.update_or_create(
            user=user,
            defaults=dict(
                nationality=Country(country_code),
                home_university=university if not faculty else None,
                home_faculty=faculty,
            ),
        )
        secho(f"Processed {i: >4}: {email}.")


def load(cursor: CursorWrapper):
    with transaction.atomic(using="legacydb"):
        load_users(cursor=cursor)


@click.command()
def load_legacy_data():
    with connections["legacydb"].cursor() as cursor:
        load(cursor=cursor)
