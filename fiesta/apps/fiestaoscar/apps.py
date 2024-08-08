from __future__ import annotations

from oscar.config import Shop as OscarShop


class OscarConfig(OscarShop):
    def get_urls(self):
        urls = super().get_urls()
        # TODO: dashboard?
        # for urlpattern in urls[:]:
        #     if hasattr(urlpattern, "app_name") and (urlpattern.app_name == "dashboard"):
        #         urls.remove(urlpattern)
        return self.post_process_urls(urls)
