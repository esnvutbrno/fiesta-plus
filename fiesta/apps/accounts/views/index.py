from __future__ import annotations

# class BuddySystemEntrance(EnsureInSectionSpaceViewMixin, PluginConfigurationViewMixin, TemplateView):
#     def get(self, request, *args, **kwargs):
#         if self.request.membership.is_international:
#             return HttpResponseRedirect(reverse("buddy_system:new-request"))
#
#         c: BuddySystemConfiguration = self.configuration
#         if c.matching_policy_instance.can_member_match:
#             return HttpResponseRedirect(reverse("buddy_system:matching-requests"))
#
#         return HttpResponseRedirect(reverse("buddy_system:index"))
