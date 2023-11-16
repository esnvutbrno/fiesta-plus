from __future__ import annotations

from apps.fiestarequests.models import BaseRequestSystemConfiguration
from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.files.views import NamespacedFilesServeView
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.views import PluginConfigurationViewMixin
from apps.utils.models.query import Q


class BaseIssuerPictureServeView(
    PluginConfigurationViewMixin[BaseRequestSystemConfiguration],
    NamespacedFilesServeView,
):
    def get_request_queryset(self, request: HttpRequest):
        raise NotImplementedError

    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # picture is from requests placed on my section
        related_requests = self.get_request_queryset(request).filter(
            issuer__profile__picture=name,
        )

        return (
            # does have the section enabled picture displaying?
            (related_requests.exists() and self.configuration and self.configuration.display_issuer_picture)
            # or are we in a matched request?
            or (
                related_requests.filter(
                    state=BaseRequestProtocol.State.MATCHED,
                )
                .filter(match__matcher=request.user)
                .exists()
            )
            # or am I the issuer?
            or (related_requests.filter(issuer=request.user).exists())
        )


class BaseMatcherPictureServeView(
    PluginConfigurationViewMixin[BaseRequestSystemConfiguration],
    NamespacedFilesServeView,
):
    def get_request_queryset(self, request: HttpRequest):
        raise NotImplementedError

    def has_permission(self, request: HttpRequest, name: str) -> bool:
        # is the file in requests, for whose is the related section responsible?
        related_requests = self.get_request_queryset(request).filter(
            match__matcher__profile__picture=name,
        )

        # does have the section enabled picture displaying?
        return (
            related_requests.filter(
                state=BaseRequestProtocol.State.MATCHED,
            )
            .filter(
                Q(match__matcher=request.user) | Q(issuer=request.user),
            )
            .exists()
        )
