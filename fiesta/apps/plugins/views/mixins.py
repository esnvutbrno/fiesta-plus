from typing import Protocol, TypeVar, Generic

from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import BasePluginConfiguration


class HasRequestProtocol(Protocol):
    request: HttpRequest


T = TypeVar("T", bound=BasePluginConfiguration)


class PluginConfigurationViewMixin(Generic[T]):
    @property
    def configuration(self: HasRequestProtocol) -> T:
        return self.request.plugin and self.request.plugin.configuration

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["configuration"] = self.configuration
        return data
