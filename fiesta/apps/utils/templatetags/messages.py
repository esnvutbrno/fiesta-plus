from __future__ import annotations

from django import template
from django.contrib.messages.storage.base import Message
from django.template import loader

register = template.Library()


@register.filter
def message_to_template(message: Message):
    return loader.get_template(f'fiesta/parts/messages/{message.level_tag or "base"}.html')
