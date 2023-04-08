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
    ("football", "⚽ Football"),
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
    ("writing", "✍️ Writing"),
    ("gaming", "🎮 Gaming"),
    ("cooking", "🍳 Cooking"),
    ("baking", "🧁 Baking"),
    ("painting", "🎨 Painting"),
    ("drawing", "✏️ Drawing"),
    ("sewing", "🧵 Sewing"),
    ("knitting", "🧶 Knitting"),
    ("crocheting", "🪡 Crocheting"),
    ("pottery", "🏺 Pottery"),
    ("sculpture", "🗿 Sculpture"),
    ("woodworking", "🪵 Woodworking"),
    ("metalworking", "🔨 Metalworking"),
    ("coding", "💻 Coding"),
    ("web_development", "🌐 Web Development"),
    ("graphic design", "🎨 Graphic Design"),
    ("animation", "🎬 Animation"),
    ("filmmaking", "🎥 Filmmaking"),
    ("acting", "🎭 Acting"),
    ("singing", "🎤 Singing"),
    ("karaoke", "🎤 Karaoke"),
    ("video_editing", "🎞️ Video Editing"),
    ("podcasting", "🎙️ Podcasting"),
    ("biking", "🚴 Biking"),
    ("skateboarding", "🛹 Skateboarding"),
    ("surfing", "🏄 Surfing"),
    ("snowboarding", "🏂 Snowboarding"),
    ("skiing", "⛷️ Skiing"),
    ("swimming", "🏊 Swimming"),
    ("diving", "🤿 Diving"),
    ("rock_climbing", "🧗 Rock Climbing"),
    ("parkour", "🤸 Parkour"),
    ("basketball", "🏀 Basketball"),
    ("soccer", "⚽ Soccer"),
    ("tennis", "🎾 Tennis"),
    ("golf", "⛳ Golf"),
    ("table_tennis", "🏓 Table Tennis"),
    ("badminton", "🏸 Badminton"),
    ("cricket", "🏏 Cricket"),
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
        blank=True,
    )

    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request")
        verbose_name_plural = _("buddy requests")

    def __str__(self):
        return f"Buddy Request {self.issuer}: {self.get_state_display()}"
