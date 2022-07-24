# Define your urls here
from django.urls import path

from apps.sections.views.choose_space import ChooseSpaceView

urlpatterns = [path("choose-section", ChooseSpaceView.as_view(), name="choose-space")]
