from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import base_request_model_factory
from apps.utils.models.fields import ArrayFieldWithDisplayableChoices

INTERESTS_CHOICES = {
    ("music", "🎶 Music"),
    ("photo", "📸 Photography"),
    ("IT", "🧑‍💻 IT"),
    ("party", "🎉 Partying"),
    ("food", "🍲 Food"),
    ("coffee", "☕ Coffee"),
    ("travel", "✈ Travelling"),
    ("dance", "💃 Dancing"),
    ("video-making", "🎥 Video-making"),
    ("footbal", "⚽ Football"),
    ("movies", "🎞️ Movies"),
    ("running", "🏃‍♀️ Running"),
    ("reading", "📚️ Reading"),
    ("shopping", "🛍️️ Shopping"),
    ("hiking", "⛰️ Hiking"),
    ("pets", "🐕️ Pets"),
    ("volleyball", "🏐️ Volleyball"),
    ("self-development", "🧑📚️ Self-development"),
    ("theatre", "🎭️ Theatre"),
    ("yoga", "🧘️ Yoga"),
    ("fashion", "🧥️ Fashion"),
    ("architecture", "🏛️️ Architecture"),
    ("tik-tok", "🤡️️ TikTok scrolling"),
}

BaseRequestForBuddySystem = base_request_model_factory(related_base="buddy_system")


class BuddyRequest(BaseRequestForBuddySystem):
    interests = ArrayFieldWithDisplayableChoices(
        base_field=CharField(
            choices=INTERESTS_CHOICES,
            max_length=24,
            # inner field could be empty (default to remove empty option in .choices)
            default=None,
        ),
        verbose_name=_("issuer interests"),
        default=list,  # as callable to not share instance,
    )

    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request")
        verbose_name_plural = _("buddy requests")

    def __str__(self):
        return f"Buddy Request {self.issuer}: {self.get_state_display()}"
