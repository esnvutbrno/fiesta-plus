from django.core.validators import RegexValidator
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _

lowercase_plain_slug_re = _lazy_re_compile(r'^[a-z]+\Z')

validate_plain_slug_lowercase = RegexValidator(
    lowercase_plain_slug_re,
    # Translators: lowercase "letters" means latin letters: a-z.
    _('Enter a valid “slug” consisting of lowercase letters.'),
    'invalid'
)