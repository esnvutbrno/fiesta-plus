import re

from django import template

register = template.Library()

# I know, it's not the best regex for emails
# [\w.] as [a-zA-Z0-9_.]
CENSORE_REGEX = re.compile(
    # emails
    r"^$|\S+@\S+\.\S+"
    # instagram username
    r"|@[\w.]+"
    # european phone numbers
    r"|\+?\d{1,3}[ \-]?[(]?\d{3,4}[)]?[ \-]?\d{3,4}[ \-]?\d{3,4}",
    # URL adresses SIMPLIFIED
    # r"(https?://)?([a-z\d_\-]{3,}\.)+[a-z]{2,4}(/\S*)?"
    re.VERBOSE | re.IGNORECASE,
)


@register.filter
def censore_description(description: str) -> str:
    return CENSORE_REGEX.sub("---censored---", description)
