from __future__ import annotations


def monkeypatch_image_dimensions_caching():
    from django.core.files.images import ImageFile, get_image_dimensions

    def _get_image_dimensions(self):
        from numbers import Number

        if not hasattr(self, "_dimensions_cache"):
            close = self.closed
            if self.field.width_field and self.field.height_field:
                width = getattr(self.instance, self.field.width_field)
                height = getattr(self.instance, self.field.height_field)
                # check if the fields have proper values
                if isinstance(width, Number) and isinstance(height, Number):
                    self._dimensions_cache = (width, height)
                else:
                    self.open()
                    self._dimensions_cache = get_image_dimensions(self, close=close)
            else:
                self.open()
                self._dimensions_cache = get_image_dimensions(self, close=close)

        return self._dimensions_cache

    ImageFile._get_image_dimensions = _get_image_dimensions
