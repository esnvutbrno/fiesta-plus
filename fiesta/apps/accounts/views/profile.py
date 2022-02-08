from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from apps.utils.breadcrumbs import with_breadcrumb


@with_breadcrumb(_('My Profile'))
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
