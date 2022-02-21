from apps.files.storage import NamespacedFilesStorage
from apps.files.views import NamespacedFilesServeView

app_name = "files"
urlpatterns = [
    NamespacedFilesServeView.as_url(storage=storage)
    for storage in NamespacedFilesStorage.storages
]
