import sys
from dataclasses import dataclass

import requests

from . import Plugin


@dataclass
class Link:
    link: str
    title: str


class Tagesschau(Plugin):
    filter_url = "tagesschau.de"
    base_url = "https://www.tagesschau.de/"
    api_url = "https://www.tagesschau.de/api/"

    def __init__(self, url):
        super().__init__(url)
        if self.filter_url in url:
            self.enabled = True
            self.session = requests.Session()

    def __get_mata_data(self, url):
        data_url = url.replace(self.base_url, self.api_url).replace("html", "json")
        r = self.session.get(data_url)
        if r.status_code != 200:
            raise ValueError("Error %i on getting url: %s" % (r.status_code, data_url))
        return r.json()

    @classmethod
    def __extrace_multimedia_links(cls, metadata):
        av_links = []
        av_types = set()
        for paragraph in metadata["copytext"]:
            boxes = paragraph.get("paragraphBoxes")
            if boxes:
                for box in boxes:
                    # box_type = box["boxtype"]
                    for content in box["boxcontent"]:
                        content_type = content["type"]
                        if content_type == "video":
                            media_url = content["mediadata"][2]["h264l"]
                            headline = "Video: " + content["headline"]
                            av_types.add("video")
                        elif content_type == "audio":
                            media_url = content["mediadata"][0]["mp3"]
                            headline = "Audio: " + content["headline"]
                            av_types.add("audio")
                        else:
                            continue
                        av_link = Link(media_url, headline)
                        av_links.append(av_link)
        return (av_links, av_types)

    def apply_on_item(self, item):
        if not self.enabled:
            return
        try:
            metadata = self.__get_mata_data(item.link)
        except ValueError as err:
            print(err, file=sys.stderr)
            return
        av_links, av_types = self.__extrace_multimedia_links(metadata)
        if len(av_links) > 0:
            item.description.append_links(av_links)
            item.content.append_links(av_links)
        if "video" in av_types:
            item.title += " [Video]"
        if "audio" in av_types:
            item.title += " [Audio]"


PLUGIN_CLASS = Tagesschau
