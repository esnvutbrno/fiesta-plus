from __future__ import annotations

from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpRequest as DjHttpRequest, HttpResponse
from django.urls import reverse

from ...accounts.models import User, UserProfile
from ...plugins.utils import target_plugin_app_from_resolver_match
from ...sections.middleware import UserMembershipMiddleware


class UserProfileMiddleware:
    FINISH_PROFILE_URL_NAME = "accounts:profile-finish"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: DjHttpRequest) -> HttpResponse:
        return self.get_response(request)

    @classmethod
    def process_view(cls, request: HttpRequest, view_func, view_args, view_kwargs):
        user: User = request.user

        target_app = target_plugin_app_from_resolver_match(request.resolver_match)

        if not target_app:
            # target is not a plugin page, profile is not needed to have it completed
            return

        if request.resolver_match.view_name in (
            cls.FINISH_PROFILE_URL_NAME,
        ) or UserMembershipMiddleware.should_ignore(
            target_app=target_app,
            resolver_match=request.resolver_match
        ):
            # to prevent loop, profile needs to be finished
            return

        try:
            # doesn't have profile at all, definitely needed to fill
            profile: UserProfile = user.profile
        except (UserProfile.DoesNotExist, AttributeError):
            # redirect to profile finish page with next parameter
            return redirect_to_login(
                next=request.get_full_path(),
                login_url=reverse(cls.FINISH_PROFILE_URL_NAME),
            )

        if profile.state != profile.State.COMPLETE:
            # profile is not complete, so redirect to profile page with next= parameter
            return redirect_to_login(
                next=request.get_full_path(),
                login_url=reverse(cls.FINISH_PROFILE_URL_NAME),
            )


__all__ = ["UserProfileMiddleware", "HttpRequest"]
