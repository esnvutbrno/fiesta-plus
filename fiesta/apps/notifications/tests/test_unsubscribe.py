from __future__ import annotations

from django.core import mail
from django.core.signing import BadSignature, SignatureExpired
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.unsubscribe import generate_unsubscribe_token, verify_unsubscribe_token
from apps.utils.factories.accounts import UserFactory


class UnsubscribeTokenServiceTestCase(TestCase):
    def test_generate_unsubscribe_token_returns_string(self):
        token = generate_unsubscribe_token(user_id=123)
        self.assertIsInstance(token, str)

    def test_verify_unsubscribe_token_decodes_user_id_and_action(self):
        token = generate_unsubscribe_token(user_id=321, action="global")

        user_id, action = verify_unsubscribe_token(token)

        self.assertEqual(user_id, 321)
        self.assertEqual(action, "global")

    def test_verify_unsubscribe_token_raises_signature_expired(self):
        token = generate_unsubscribe_token(user_id=123)

        with self.assertRaises(SignatureExpired):
            verify_unsubscribe_token(token, max_age=-1)

    def test_verify_unsubscribe_token_raises_bad_signature_for_tampered_token(self):
        token = generate_unsubscribe_token(user_id=123)
        tampered_token = f"{token}tampered"

        with self.assertRaises(BadSignature):
            verify_unsubscribe_token(tampered_token)


class UnsubscribeViewTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(profile=None)
        self.profile = UserProfile.objects.create(user=self.user)

    def test_unsubscribe_post_sets_global_opt_out(self):
        token = generate_unsubscribe_token(user_id=self.profile.pk, action="global")

        response = self.client.post(f"/notifications/unsubscribe/{token}/")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.profile.email_notifications_enabled)

    def test_unsubscribe_get_shows_confirmation_page(self):
        token = generate_unsubscribe_token(user_id=self.profile.pk, action="global")

        response = self.client.get(f"/notifications/unsubscribe/{token}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsubscribe from Notifications")

    def test_unsubscribe_post_is_idempotent_for_already_opted_out_user(self):
        self.profile.email_notifications_enabled = False
        self.profile.save(update_fields=["email_notifications_enabled", "modified"])
        token = generate_unsubscribe_token(user_id=self.profile.pk, action="global")

        response = self.client.post(f"/notifications/unsubscribe/{token}/")

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.profile.email_notifications_enabled)


class NotificationMailerUnsubscribeHeadersTestCase(TestCase):
    def test_sent_email_contains_list_unsubscribe_headers(self):
        user = UserFactory(profile=None)
        profile = UserProfile.objects.create(user=user)

        send_notification_email(
            subject="Subject",
            recipient_email=user.email,
            template_prefix="notifications/base_email",
            context={
                "section": "ESN Test",
                "preferences_url": "https://example.com/preferences",
            },
            recipient_profile=profile,
        )

        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]

        self.assertIn("List-Unsubscribe", sent_email.extra_headers)
        self.assertIn("List-Unsubscribe-Post", sent_email.extra_headers)
        self.assertEqual(sent_email.extra_headers["List-Unsubscribe-Post"], "List-Unsubscribe=One-Click")
        self.assertIn("/notifications/unsubscribe/", sent_email.extra_headers["List-Unsubscribe"])
