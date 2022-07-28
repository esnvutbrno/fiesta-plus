from django.db.models.manager import Manager


class FacultyManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("university")
