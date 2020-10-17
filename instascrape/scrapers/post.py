from __future__ import annotations

# pylint: disable=no-member

import datetime
from typing import List, Any
import abc

from instascrape.core._static_scraper import _StaticHtmlScraper
from instascrape.core._mappings import _PostMapping


class Post(_StaticHtmlScraper):
    """
    Scraper for an Instagram post page

    Attributes
    ----------
    _Mapping
        Mapping class with directives specific to scraping JSON from an
        Instagram post page

    Methods
    -------
    from_shortcode(shortcode: str) -> Post
        Factory method that returns a Post object from a shortcode
    """

    _Mapping = _PostMapping

    def load(self, keys: List[str] = [], exclude: List[str] = []):
        super().load(keys=keys)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)

    def to_json(self, fp: str, metadata: bool = False):
        # have to convert to serializable format
        self.upload_date = datetime.datetime.timestamp(self.upload_date)
        super().to_json(fp=fp, metadata=metadata)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)

    def to_csv(self, fp: str, metadata: bool = False):
        # have to convert to serializable format
        self.upload_date = datetime.datetime.timestamp(self.upload_date)
        super().to_csv(fp=fp, metadata=metadata)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)

    @classmethod
    def from_shortcode(cls, shortcode: str) -> Post:
        url = f"https://www.instagram.com/p/{shortcode}/"
        return cls(url, name=shortcode)
