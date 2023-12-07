from __future__ import annotations

from typing import TypedDict

from django.core.exceptions import ObjectDoesNotExist
from elasticsearch import Elasticsearch, Transport, Urllib3HttpConnection

from apps.wiki import models


class Revision(TypedDict):
    at: str
    name: str
    email: str
    sha: str
    parent_sha: str


class Page(TypedDict):
    content_html: str
    content_plain: str
    toc: str
    title: str
    file: str

    last_change: Revision


class SearchPage(TypedDict):
    source: Page
    score: float
    highlight: list[str]


class ElasticAdapter:
    def __init__(self, client: Elasticsearch):
        self._client = client

    @staticmethod
    def split_path(path: str) -> tuple[str, str]:
        return path.rpartition("/")[::2]

    def get_page_parts(self, path: str) -> tuple[Page | None, Page | None]:
        base, _ = self.split_path(path)
        return (
            self._page_for_filename("_Sidebar", base=base),
            self._page_for_filename("_Footer", base=base),
        )

    def page_for_path(self, path: str) -> Page | None:
        path = path.strip("/")
        base, file_name = self.split_path(path)

        if file_name:
            page = self._page_for_filename(file_name=file_name, base=base)
            if not page:
                raise ObjectDoesNotExist()

            return page

        return self._page_for_filename("Home", base=base)

    def search(self, term: str) -> list[SearchPage]:
        results = self._client.search(
            index="wiki",
            query={
                "match_phrase": {
                    "content_plain": term.strip(),
                },
                # "multi_match": {
                #     "query": q,
                #     "fields": ["content_plain"],
                #     "fuzziness": "AUTO"
                # }
            },
            highlight={
                "tags_schema": "styled",
                "fields": {
                    "content_plain": {
                        "type": "unified",
                        "matched_fields": ["content_plain"],
                        "number_of_fragments": 1,
                        "fragment_size": 200,
                        # "pre_tags": ["<b>"],
                        # "post_tags": ["</b>"]
                    }
                },
            },
        )
        return [
            SearchPage(source=hit["_source"], highlight=hit["highlight"], score=hit["_score"])
            for hit in results["hits"]["hits"]
        ]

    def _page_for_filename(self, file_name: str, *, base: str = "") -> Page | None:
        base = f"{base}/" if base else ""

        hits = self._client.search(
            index="wiki",
            query=dict(
                prefix={
                    "file.keyword": f"{base}{file_name}.",
                }
            ),
        )[
            "hits"
        ]["hits"]

        if hits:
            return hits[0]["_source"]
        return None


class LocalDbAdapter(ElasticAdapter):
    def _page_for_filename(self, file_name: str, *, base: str = "") -> Page | None:
        base = f"{base}/" if base and not file_name.startswith("_") else ""
        return models.Page.objects.using("wiki").get(file__contains=f"{base}{file_name}.").__dict__

    def search(self, term: str) -> list[SearchPage]:
        results = models.Page.objects.using("wiki").raw(
            """
                SELECT
                    snippet(wiki, 1, '<b>', '</b>', '...', 64) as highlight,
                    rank as rank,
                    w.*
                FROM wiki AS w
                WHERE content_plain MATCH %s
                ORDER BY rank;
            """,
            [term.strip()],
        )

        return [
            SearchPage(
                source=page.__dict__,
                highlight=page.highlight,
                score=page.rank,
            )
            for page in results
            if not page.file.startswith("_")
        ]


class LocalCATrustedTransportation(Transport):
    # TODO: really here?
    class CATrustedConnection(Urllib3HttpConnection):
        def __init__(self, *args, **kwargs) -> None:
            kwargs["ca_certs"] = "/usr/share/certs/rootCA.pem"
            super().__init__(*args, **kwargs)

    DEFAULT_CONNECTION_CLASS = CATrustedConnection


es = Elasticsearch(
    hosts=["https://elastic:elastic@elastic:9200"],
    transport_class=LocalCATrustedTransportation,
)

wiki_adapter = LocalDbAdapter(client=es)
# wiki_adapter = ElasticAdapter(client=es)
