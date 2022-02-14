from django.forms import model_to_dict

from apps.accounts.forms.profile_finish import UserProfileForm
from apps.accounts.models import AccountsConfiguration, UserProfile
from apps.sections.models import SectionMembership


class UserProfileStateSynchronizer:
    """
    Defines synchronization behaviour for `UserProfile.state` attribute
    regarding AccountsConfiguration for each Section.
    """

    @staticmethod
    def on_user_profile_update(profile: UserProfile):
        """
        User profile of user was updated, so it's needed to resolve new state for profile.

        User probably has not just one section membership, so not only one accounts configuration.
        """

        # assumes profile is fine for all possible configurations
        final_state = UserProfile.State.COMPLETE

        # UserProfile form is here as validator
        form_class = UserProfileForm.for_user(user=profile.user)
        form = form_class(
            instance=profile,
            data=model_to_dict(
                profile, form_class._meta.fields, form_class._meta.exclude
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

        profile.state = final_state
        profile.save(update_fields=["state"], skip_hooks=True)

    @classmethod
    def on_accounts_configuration_update(cls, conf: AccountsConfiguration):
        """
        After change of Accounts configuration, checks all COMPLETED profiles if they're fine for new configuration.
        If not, profile is set to UNCOMPLETED.
        Implements only change to more strict conditions, which is O(n).

        Implementation with less strict conditions leads to O(n^2).
        """
        # for each connected user profile
        for profile in UserProfile.objects.filter(
            user__memberships__section__plugins__configuration=conf,
            state=UserProfile.State.COMPLETE,
        ):
            cls.on_user_profile_update(profile=profile)

    @classmethod
    def on_membership_update(cls, membership: SectionMembership):
        try:
            # membership could be created for user without profile (usually the first one membership)
            profile: UserProfile = membership.user.profile
        except UserProfile.DoesNotExist:
            return

        return cls.on_user_profile_update(profile=profile)


__all__ = ["UserProfileStateSynchronizer"]
