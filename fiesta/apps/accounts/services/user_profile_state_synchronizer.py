from __future__ import annotations

import functools
import logging
from contextlib import contextmanager

from django.core.exceptions import ValidationError
from django.forms import model_to_dict

from apps.accounts.forms.profile import FIELDS_FROM_USER
from apps.accounts.forms.profile_factory import UserProfileFormFactory
from apps.accounts.models import UserProfile
from apps.sections.models import SectionMembership, SectionsConfiguration

logger = logging.getLogger(__name__)


def _if_enabled(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.ENABLED:
            return func(self, *args, **kwargs)
        return None

    return wrapper


class UserProfileStateSynchronizer:
    """
    Defines synchronization behaviour for `UserProfile.state` attribute
    regarding AccountsConfiguration for each Section.
    """

    ENABLED = True

    @_if_enabled
    def revalidate_user_profile(self, profile: UserProfile):
        """
        User profile of user was updated, so it's needed to resolve new state for profile.

        User probably has not just one section membership, so not only one accounts configuration.
        """

        # assumes profile is fine for all possible configurations
        final_state = UserProfile.State.COMPLETE

        # UserProfile form is here as validator
        form_class = UserProfileFormFactory.for_user(user=profile.user)
        form = form_class(
            instance=profile,
            data=model_to_dict(
                profile,
                form_class.base_fields,
                form_class._meta.exclude,
            )
            | model_to_dict(
                profile.user,
                FIELDS_FROM_USER,
            ),
        )

        # make the form bounded, so it thinks it¨s connected to data
        # and performs full clean to validate instance
        form.is_bound = True
        form.full_clean()
        # cannot use is_valid(), since it checks for bounded data (and we have no incoming data)
        if form.errors:
            # for this specific accounts conf, profile is not OK,
            # so final state leds to incomplete
            final_state = UserProfile.State.INCOMPLETE
            logger.info("Profile is not valid: %s", form.errors)

        try:
            # validate also model itself
            profile.full_clean()
        except ValidationError as e:
            logger.info("Profile is not valid: %s", e)
            final_state = UserProfile.State.INCOMPLETE

        profile.state = final_state
        profile.enforce_revalidation = False
        profile.save(update_fields=["state", "enforce_revalidation"], skip_hooks=True)

    @_if_enabled
    def on_accounts_configuration_update(self, conf: SectionsConfiguration):
        """
        After change of Accounts configuration, mark all related user profiles for revalidation.
        """
        # for each connected user profile enforce revalidation
        UserProfile.objects.filter(
            user__memberships__section__plugins__configuration=conf,
            state=UserProfile.State.COMPLETE,
        ).update(enforce_revalidation=True)

    @_if_enabled
    def on_membership_update(self, membership: SectionMembership):
        try:
            # membership could be created for user without profile (usually the first one membership)
            profile: UserProfile = membership.user.profile
        except UserProfile.DoesNotExist:
            return None

        return self.revalidate_user_profile(profile=profile)

    @contextmanager
    def without_profile_revalidation(self):
        prev = self.ENABLED
        self.ENABLED = False
        yield
        self.ENABLED = prev


synchronizer = UserProfileStateSynchronizer()

__all__ = ["synchronizer"]
