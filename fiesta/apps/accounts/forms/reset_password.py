from __future__ import annotations

from allauth.account.forms import ResetPasswordForm as BaseResetPasswordForm


class ResetPasswordForm(BaseResetPasswordForm):
    def _send_unknown_account_mail(self, request, email):
        # allauth==0.54.0 sends an email in case of password reset and email not found
        # we override this method to prevent sending email in case of email not founding

        return
