from __future__ import annotations

from apps.files.storage import NamespacedFilesStorage


class EditorImagesStorage(NamespacedFilesStorage):
    """Used for all images uploaded from editorjs interface, has to be defined as class."""

    def __init__(self):
        super().__init__(location="editor-images", has_permission=lambda *_: True)
