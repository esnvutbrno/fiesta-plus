from __future__ import annotations

from datetime import timedelta

import factory
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.accounts.models import UserProfile
from apps.notifications.models import NotificationKind, ScheduledNotification, SectionNotificationPreferences


def _create_profile(_obj):
    """Create a UserProfile for a fresh user, avoiding the broken UserProfileFactory."""
    from apps.utils.factories.accounts import UserFactory

    user = UserFactory(profile=None)
    return UserProfile.objects.create(user=user)


class ScheduledNotificationFactory(DjangoModelFactory):
    """Creates a pending (not yet sent, not cancelled) ScheduledNotification."""

    class Meta:
        model = ScheduledNotification

    kind = NotificationKind.BUDDY_MATCHED_ISSUER
    recipient = factory.SubFactory("apps.utils.factories.accounts.UserFactory", profile=None)
    section = factory.SubFactory("apps.utils.factories.sections.KnownSectionFactory")

    # Generic FK fields — point to a section by default (simple object that always exists)
    content_type = factory.LazyAttribute(lambda obj: ContentType.objects.get_for_model(obj.section.__class__))
    object_id = factory.LazyAttribute(lambda obj: obj.section.pk)

    send_after = factory.LazyFunction(lambda: timezone.now() - timedelta(minutes=5))
    sent_at = None
    cancelled_at = None


class SectionNotificationPreferencesFactory(DjangoModelFactory):
    """Creates per-user, per-section notification preferences."""

    class Meta:
        model = SectionNotificationPreferences
        django_get_or_create = ("user", "section")

    user = factory.SubFactory("apps.utils.factories.accounts.UserFactory")
    section = factory.SubFactory("apps.utils.factories.sections.KnownSectionFactory")

    notify_on_match = True
    notify_on_new_member_waiting = True
