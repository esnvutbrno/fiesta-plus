from __future__ import annotations

from django.test import TestCase

WHATSAPP_LINKS = [
    ("https://wa.me/420777756789", "420777756789"),
    ("https://wa.me/420777756789?text=Hello", "420777756789"),
    ("https://wa.me/420777756789?text=Hello%20World", "420777756789"),
    ("+420777756789", "420777756789"),
    ("+420 777 756 789", "420777756789"),
]


class SocialAccountsFieldsTestCase(TestCase):
    def test_clean_whatsapp(self):
        from apps.accounts.forms.social_accounts_fields import clean_whatsapp

        for link, expected in WHATSAPP_LINKS:
            with self.subTest(link=link, expected=expected):
                self.assertEqual(clean_whatsapp(link), expected)
