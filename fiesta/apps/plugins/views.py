from typing import Protocol, TypeVar, Generic

from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import BasePluginConfiguration


class HasRequestProtocol(Protocol):
    request: HttpRequest


T = TypeVar('T', bound=BasePluginConfiguration)


class PluginConfigurationViewMixin(Generic[T]):
    @property
    def configration(self: HasRequestProtocol) -> T:
        return self.request.plugin.configuration
