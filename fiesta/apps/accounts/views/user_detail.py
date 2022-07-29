from operator import attrgetter

from django.views.generic import DetailView

from apps.accounts.models import AccountsConfiguration
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.models import SectionMembership
from apps.utils.breadcrumbs import with_object_breadcrumb


@with_object_breadcrumb(getter=attrgetter("user.full_name"))
class UserDetailView(
    PluginConfigurationViewMixin[AccountsConfiguration],
    DetailView,
):
    model = SectionMembership
    template_name = "accounts/user_detail/user_detail.html"
