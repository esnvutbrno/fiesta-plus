from apps.accounts.forms.profile_finish import UserProfileForm
from apps.accounts.models import AccountsConfiguration, UserProfile


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
        configurations = AccountsConfiguration.objects.filter(
            plugin__section__memberships__user=profile.user,
        )

        # assumes profile is fine for all possible configurations
        final_state = UserProfile.State.COMPLETE

        for conf in configurations:  # type: AccountsConfiguration
            # UserProfile form is here as validator
            form = UserProfileForm.from_accounts_configuration(conf=conf)(
                instance=profile,
                # data=dict(),
            )

            # cannot use is_valid(), since it checks for bounded data (and we have no incoming data)
            if form.errors:
                # for this specific accounts conf, profile is not OK,
                # so final state leds to incomplete
                final_state = UserProfile.State.INCOMPLETE
                break

        profile.state = final_state
        profile.save(update_fields=["state"], skip_hooks=True)

    @staticmethod
    def on_accounts_configuration_update(conf: AccountsConfiguration):
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
            final_state = profile.state

            form = UserProfileForm.from_accounts_configuration(conf=conf)(
                instance=profile,
            )

            # cannot use is_valid(), since it checks for bounded data (and we have no incoming data)
            if form.errors:
                # for this specific accounts conf, profile is not OK,
                # so final state leds to incomplete
                final_state = UserProfile.State.INCOMPLETE

            profile.state = final_state
            profile.save(update_fields=["state"], skip_hooks=True)


__all__ = ["UserProfileStateSynchronizer"]
