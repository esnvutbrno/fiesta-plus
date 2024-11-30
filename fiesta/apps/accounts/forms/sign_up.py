from __future__ import annotations

from allauth.account.forms import SignupForm as AllauthSignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3


class SignupForm(AllauthSignupForm):
    recaptcha = ReCaptchaField(
        widget=ReCaptchaV3(
            action="signup",
            attrs={"theme": "clean"},
        )
    )
