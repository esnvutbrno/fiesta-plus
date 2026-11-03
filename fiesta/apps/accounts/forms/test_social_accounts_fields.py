from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

WHATSAPP_LINKS = [
    ("https://wa.me/420777756789", "420777756789"),
    ("https://wa.me/420777756789?text=Hello", "420777756789"),
    ("https://wa.me/420777756789?text=Hello%20World", "420777756789"),
    ("+420777756789", "420777756789"),
    ("+420 777 756 789", "420777756789"),
    # Iceland has seven-digit numbers (#227)
    ("+354 611 1234", "3546111234"),
    ("+3544101234", "3544101234"),
]

# no Icelandic number starts with 1, 2 or 3 at seven digits
INVALID_ICELAND_NUMBER = "+354 123 4567"


class SocialAccountsFieldsTestCase(TestCase):
    def test_clean_whatsapp(self):
        from apps.accounts.forms.social_accounts_fields import clean_whatsapp

        for link, expected in WHATSAPP_LINKS:
            with self.subTest(link=link, expected=expected):
                self.assertEqual(clean_whatsapp(link), expected)

    def test_clean_whatsapp_rejects_unassigned_number(self):
        from apps.accounts.forms.social_accounts_fields import clean_whatsapp

        with self.assertRaises(ValidationError):
            clean_whatsapp(INVALID_ICELAND_NUMBER)

    def test_profile_phone_number_accepts_iceland(self):
        from apps.accounts.models import UserProfile

        field = UserProfile._meta.get_field("phone_number").formfield()

        self.assertEqual(field.clean("+354 611 1234").as_e164, "+3546111234")
        with self.assertRaises(ValidationError):
            field.clean(INVALID_ICELAND_NUMBER)
