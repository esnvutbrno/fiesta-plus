import re

from django import template

register = template.Library()

# I know, it's not the best regex for emails
# [\w.] as [a-zA-Z0-9_.]
CENSORE_REGEX = re.compile(
    r"\S+@\S+\.\S+|" r"@[\w.]+", re.VERBOSE  # emails  # ig username with @...
)


@register.filter
def censore_description(description: str) -> str:
    return CENSORE_REGEX.sub("---censored---", description)
