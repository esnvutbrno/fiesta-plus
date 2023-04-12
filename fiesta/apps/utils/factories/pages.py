from __future__ import annotations

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyAttribute, FuzzyChoice

from apps.pages.models.page import Page
from apps.sections.models import Section


class PageFactory(DjangoModelFactory):
    class Meta:
        model = Page

    parent = FuzzyChoice(
        tuple(Page.objects.filter(level=0)) + 2 * (None,),
    )

    section = FuzzyChoice(
        Section.objects.all(),
    )

    title = factory.Faker("text", max_nb_chars=12)

    order = factory.Sequence(lambda f: f)

    content = FuzzyAttribute(
        lambda: {
            "time": 1550476186479,
            "blocks": [
                {
                    "type": "paragraph",
                    "data": {"text": "The example of text that was written in <b>one of popular</b> text editors."},
                },
                {"type": "header", "data": {"text": "With the header of course", "level": 2}},
                {"type": "paragraph", "data": {"text": "So what do we have?"}},
            ],
            "version": "2.8.1",
        }
    )
