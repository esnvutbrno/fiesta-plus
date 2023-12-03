from __future__ import annotations

from django.contrib import admin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import Event, EventsConfiguration, Organizer, Participant, Place, PriceVariant
from apps.plugins.models import BasePluginConfiguration


@admin.register(EventsConfiguration)
class EventsConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    list_display = (
        "name",
        "section",
        "shared",
        "require_confirmation",
        "members_can_create",
        "online_purchases",
    )
    show_in_index = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("section", "title", "capacity", "state", "start", "end", "author", "place")
    show_in_index = True

    # @admin.display(
    #     description=_("Filled"),
    # )
    # def filled(self, obj: Section):
    # return obj.memberships.count()
    # TODO


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "role")
    show_in_index = True


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "price", "created")
    show_in_index = True


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "link", "map_link", "section")
    show_in_index = True


@admin.register(PriceVariant)
class PriceVariantAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "amount", "event", "available_from", "available_to")
    show_in_index = True
