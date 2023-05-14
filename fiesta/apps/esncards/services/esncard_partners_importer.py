from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class EsnCardPartnersImporter:
    API_URL = "https://esncard.org/discover/list?query=&page={page}"

    def sync(self):
        page = 1

        while True:
            response = requests.get(self.API_URL.format(page=page))

            if response.status_code == 400:
                break

            markup = BeautifulSoup(response.text, "html.parser")

            self._sync_from_page(page=markup)

            page += 1

    def _sync_from_page(self, page: BeautifulSoup):
        for partner in page.select(".discount-list-item"):
            title = partner.select_one("h3").text

            logger.info(title)
