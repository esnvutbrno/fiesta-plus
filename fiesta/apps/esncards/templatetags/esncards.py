from django import template

from apps.plugins.middleware.plugin import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_esncard_application_of_user(context):
    request: HttpRequest = context["request"]

    # TODO: could be more then one?
    return request.membership.user.esncard_applications.filter(
        section=request.membership.section,
    ).first()
