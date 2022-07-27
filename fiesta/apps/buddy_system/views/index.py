from django.views.generic import TemplateView

from apps.buddy_system.models import BuddySystemConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.middleware.section_space import HttpRequest


class BuddySystemIndexView(
    PluginConfigurationViewMixin[BuddySystemConfiguration], TemplateView
):
    request: HttpRequest
    template_name = "buddy_system/index.html"
