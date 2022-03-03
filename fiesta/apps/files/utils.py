from django.db.models.fields.files import FieldFile

from apps.files.storage import NamespacedFilesStorage
from apps.utils.models import BaseModel


def copy_between_storages(
    *, from_: FieldFile, to_: FieldFile, to_instance: BaseModel
) -> str:
    """
    Takes two Django Files from model fields and copy the first one onto second one.
    :param from_: Source of copying
    :param to_: Destination field
    :param to_instance: Destination instance
    :return: new name of copied file
    """
    to_storage: NamespacedFilesStorage = to_.storage

    return to_storage.save(to_storage.upload_to(to_instance, from_.name), from_.file)
