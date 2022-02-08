from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest as DjHttpRequest, HttpResponse

from ...accounts.models import User, UserProfile
from ..models import SectionMembership


class HttpRequest(DjHttpRequest):
    membership: SectionMembership | None


class UserMembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: DjHttpRequest) -> HttpResponse:
        user: User | AnonymousUser = request.user

        if user.is_authenticated:
            # TODO: Detect, in which membership is user logged:
            #  probably the default one, with possibility to switch
            #  with sesstion flag
            request.membership = user.memberships.select_related(
                # to remove another query for relating section
                "section"
            ).first()
        else:
            request.membership = None

        try:
            user.profile
        except (UserProfile.DoesNotExist, AttributeError):
            ...
            # TODO: check, if user does have a filled profile
            #  and if not, redirect him to profile-form-page to complete the profile
            #  be aware and check, if profile-form-page is not the target one.

        response: HttpResponse = self.get_response(request)
        return response


__all__ = ["UserMembershipMiddleware", "HttpRequest"]
