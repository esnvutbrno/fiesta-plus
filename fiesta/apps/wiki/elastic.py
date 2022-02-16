from __future__ import annotations

from typing import TypedDict

from django.core.exceptions import ObjectDoesNotExist
from elasticsearch import Elasticsearch, Transport, Urllib3HttpConnection


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


class WikiElastic:
    def __init__(self, client: Elasticsearch):
        self._client = client

    def get_page_parts(self, path: str) -> tuple[Page | None, Page | None]:
        base = path.rpartition("/")[0]
        return (
            self._page_for_filename("_Sidebar", base=base),
            self._page_for_filename("_Footer", base=base),
        )

    def page_for_path(self, path: str) -> Page | None:
        path = path.strip("/")
        base, _, file_name = path.rpartition("/")

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
            SearchPage(
                source=hit["_source"], highlight=hit["highlight"], score=hit["_score"]
            )
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
        )["hits"]["hits"]

        if hits:
            return hits[0]["_source"]


class LocalCATrustedTransportion(Transport):
    # TODO: really here?
    class CATrustedConnection(Urllib3HttpConnection):
        def __init__(self, *args, **kwargs) -> None:
            kwargs["ca_certs"] = "/usr/share/certs/rootCA.pem"
            super().__init__(*args, **kwargs)

    DEFAULT_CONNECTION_CLASS = CATrustedConnection


es = Elasticsearch(
    hosts=["https://elastic:elastic@elastic:9200"],
    transport_class=LocalCATrustedTransportion,
)

wiki_elastic = WikiElastic(client=es)
