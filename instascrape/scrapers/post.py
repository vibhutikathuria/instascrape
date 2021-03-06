from __future__ import annotations

import datetime
from typing import List
import re
import shutil
import pathlib

import requests

from instascrape.core._mappings import _PostMapping
from instascrape.core._static_scraper import _StaticHtmlScraper
from instascrape.scrapers.json_tools import parse_json_from_mapping
from instascrape.scrapers.comment import Comment

class Post(_StaticHtmlScraper):
    """
    Scraper for an Instagram post page

    Methods
    -------
    from_shortcode(shortcode: str) -> Post
        Factory method that returns a Post object from a shortcode
    """

    _Mapping = _PostMapping
    SUPPORTED_DOWNLOAD_EXTENSIONS = ['.mp3', '.mp4', '.png', 'jpg']

    def download(self, fp: str) -> None:
        """
        Download an image or video from a post to your local machine at the given fpath

        Parameters
        ----------
        fp : str
            Filepath to download the image to
        """
        ext = pathlib.Path(fp).suffix
        if ext not in self.SUPPORTED_DOWNLOAD_EXTENSIONS:
            raise NameError(
                f"{ext} is not a supported file extension. Please use {', '.join(self.SUPPORTED_DOWNLOAD_EXTENSIONS)}"
            )
        url = self.video_url if self.is_video else self.display_url
        data = requests.get(url, stream=True)
        if self.is_video:
            self._download_video(fp=fp, data=data)
        else:
            self._download_photo(fp=fp, data=data)

    def _download_photo(self, fp: str, data):
        with open(fp, 'wb') as outfile:
            shutil.copyfileobj(data.raw, outfile)

    def _download_video(self, fp: str, data):
        with open(fp, 'wb') as outfile:
            for chunk in data.iter_content(chunk_size=1024):
                    if chunk:
                        outfile.write(chunk)
                        outfile.flush()

    def load(self, keys: List[str] = [], exclude: List[str] = []):
        super().load(keys=keys)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)
        self.tagged_users = self._parse_tagged_users(self.json_dict)
        self.hashtags = self._parse_hashtags(self.caption)

    def to_json(self, fp: str):
        # have to convert to serializable format
        self.upload_date = datetime.datetime.timestamp(self.upload_date)
        super().to_json(fp=fp)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)

    def to_csv(self, fp: str):
        # have to convert to serializable format
        self.upload_date = datetime.datetime.timestamp(self.upload_date)
        super().to_csv(fp=fp)
        self.upload_date = datetime.datetime.fromtimestamp(self.upload_date)

    @classmethod
    def load_from_mapping(self, json_dict, map_dict):
        data_dict = parse_json_from_mapping(json_dict, map_dict)
        post = Post.from_shortcode(data_dict["shortcode"])
        for key, val in data_dict.items():
            setattr(post, key, val)
        # TODO: Bad encapsulation, figure a better way of handling timestamp
        post.upload_date = datetime.datetime.fromtimestamp(post.upload_date)
        return post

    def get_recent_comments(self):
        list_of_dicts = self.json_dict['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']
        comments_arr = [Comment(comment_dict) for comment_dict in list_of_dicts]
        return comments_arr

    def _parse_tagged_users(self, json_dict) -> List[str]:
        """Parse the tagged users from JSON dict containing the tagged users"""
        tagged_arr = json_dict['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_tagged_user']['edges']
        return [node['node']['user']['username'] for node in tagged_arr]

    def _parse_hashtags(self, caption) -> List[str]:
        """Parse the hastags from the post's caption using regex"""
        pattern = r"#(\w+)"
        return re.findall(pattern, caption)

    @classmethod
    def from_shortcode(cls, shortcode: str) -> Post:
        url = f"https://www.instagram.com/p/{shortcode}/"
        return cls(url, name=shortcode)
