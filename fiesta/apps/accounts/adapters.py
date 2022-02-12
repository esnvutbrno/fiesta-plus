from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest
from django_htmx.http import HttpResponseClientRedirect


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    ...


class AccountAdapter(DefaultAccountAdapter):
    def is_ajax(self, request: HttpRequest):
        return super().is_ajax(request) or request.htmx

    def ajax_response(self, request, response, redirect_to=None, form=None, data=None):
        if not request.htmx or not redirect_to:
            return super().ajax_response(request, response, redirect_to=redirect_to, form=form, data=data)

        if redirect_to:
            return HttpResponseClientRedirect(redirect_to=redirect_to)
