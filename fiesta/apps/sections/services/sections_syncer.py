import re
import typing
from typing import TypedDict

import requests
from click import secho
from django.utils.text import slugify

from apps.sections.models import Section, SectionUniversity
from apps.universities.models import University


class SectionData(TypedDict):
    label: str
    code: str
    website: str
    cc: str
    university_name: str

    state: typing.Literal[
        "active",
        "merged",
        "warned",
        "withdrew",
    ]


class SectionsSyncer:
    """

    {
       "label": "ESN VUT Brno",
       "code": "CZ-BRNO-VUT",
       "website": "https://esnvutbrno.cz/",
       "country": "Czechia",
       "cc": "CZ",
       "state": "active",
       "address": {
         "street_address": "Kolejní 2906/4\r\n612 00\r\nBrno\r\nCzechia",
         "locality": "Brno",
         "postal_code": "612 00",
         "country": "Czechia"
       },
       "cities": [
         {
           "name": "Brno",
           "cc": "CZ"
         }
       ],
       "geolocation": {
         "lat": "49.2311847",
         "lng": "16.5736247",
         "lat_sin": 0.7573505844605075,
         "lat_cos": 0.6530084932199027,
         "lng_rad": 0.2892643200048574
       },
       "university_name": "Brno University of Technology",
       "university_website": "https://www.vutbr.cz/en/",
       "updated": "1639496271",
       "facebook": "https://www.facebook.com/esn.vut.brno/",
       "instagram": "https://www.instagram.com/esnvutbrno/",
       "twitter": "",
       "video": "https://www.youtube.com/watch?v=pMPFoxjdXOI",
       "logo": "/sites/default/files/logos/CZ-BRNO-VUT.png"
     }
    """

    URL: str = "https://accounts.esn.org/api/v2/sections"

    def sync(self):
        response = requests.get(self.URL)

        response.raise_for_status()

        for section_data in response.json():
            self._sync_section(data=section_data)

    def _sync_section(self, data: SectionData) -> Section:
        secho(f"Syncing {data.get('code')}")
        section, _ = Section.objects.update_or_create(
            code=data.get("code"),
            name=data.get("label"),
            defaults=dict(
                space_slug=slugify(data.get("label")).replace("-", ""),
                country=data.get("cc"),
            ),
        )

        university_name = data.get("university_name")
        if not university_name or "," in university_name:
            secho(f"Skipping university: {university_name}")
            return section

        abbr = "".join(re.findall(r"^[A-Z]| [A-Z]", university_name)).replace(" ", "")
        secho(f"Syncing {university_name}: {abbr}")
        university, _ = University.objects.update_or_create(
            abbr=abbr,
            defaults=dict(
                name=university_name,
                country=data.get("cc"),
            ),
        )
        SectionUniversity.objects.update_or_create(
            section=section,
            university=university,
        )

        return section
