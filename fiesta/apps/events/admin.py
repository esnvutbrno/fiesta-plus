from django.contrib import admin
from apps.plugins.models import BasePluginConfiguration

from .models import EventsConfiguration, Event, Organizer, Participant, Place, PriceVariant
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(EventsConfiguration)
class EventsConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
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
    list_display = ("user", "event", "state")
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
