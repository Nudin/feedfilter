#
#  feedfilter - remove duplicates and uninteresting stuff in news-feeds
#  Copyright (C) 2016 Michael F. Schoenitzer
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import re
import sys
import xml.etree.ElementTree as etree
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Iterator

from utils import append_to_html

RSS_URL = "http://purl.org/rss/1.0/modules/content/"
ATOM_URL = "http://www.w3.org/2005/Atom"
XML_URL = "http://www.w3.org/XML/1998/namespace"


def get_feed(feed_file):
    """
    Determin the format of the feed and parse it
    """
    tree = etree.parse(feed_file)
    root = tree.getroot()
    if root.tag == "{%s}feed" % ATOM_URL:
        return AtomFeed(tree)
    if root.tag == "rss":
        return RssFeed(tree)
    raise NotImplementedError("Unknown feedformat!")


class Content:
    """
    Represents one item of a feed.
    """

    def __init__(self, item):
        self.item = item

    @property
    @abstractmethod
    def title(self):
        """
        The title of the news-item
        """

    @title.setter
    @abstractmethod
    def title(self, newtitle):
        """
        Set the title of the news-item
        """

    @property
    @abstractmethod
    def description(self):
        """
        The description of the news-item
        """

    @description.setter
    @abstractmethod
    def description(self, text):
        """
        Set the description
        """

    def append_description(
        self,
        text,
        html=True,
        tag="p",
        containertag="div",
        containername=None,
    ):
        """
        Append the given text to the description
        """
        original_content = self.description
        new_content = self.__append_textorhtml__(
            original_content,
            text,
            html=html,
            tag=tag,
            containertag=containertag,
            containername=containername,
        )
        self.description = new_content

    def add_crosslink(self, link, title):
        """
        Append the given link to the description and content under an heading "see also"
        """
        fulllink = '<a href="' + link + '">' + title + "</a>"
        self.append_description(
            fulllink,
            html=True,
            containername="crosslink",
            containertag="ul",
            tag="li",
        )
        self.append_content(
            fulllink,
            html=True,
            containername="crosslink",
            containertag="ul",
            tag="li",
        )

        if re.match(r"\[\+\d\]", self.title[-4:]):
            num = int(self.title[-2]) + 1
            self.title = self.title[:-4] + "[+%i]" % num
        else:
            self.title = self.title + " [+1]"

    @property
    @abstractmethod
    def content(self):
        """
        The content of the news-item
        """

    @content.setter
    @abstractmethod
    def content(self, text):
        """
        Set the content of the news-item
        """

    @staticmethod
    def __append_textorhtml__(
        original_content,
        text,
        html=False,
        tag="p",
        containertag="div",
        containername=None,
    ):
        try:
            return append_to_html(
                original_content, text, html, tag, containertag, containername
            )
        except Exception as e:
            new_content = original_content + text
            return new_content

    def append_content(
        self,
        text,
        html=True,
        tag="p",
        containertag="div",
        containername=None,
    ):
        """
        Append the given text to the content
        """
        original_content = self.content
        new_content = self.__append_textorhtml__(
            original_content,
            text,
            html=html,
            tag=tag,
            containertag=containertag,
            containername=containername,
        )
        self.content = new_content

    @property
    @abstractmethod
    def link(self):
        """
        The link of the news-item
        """

    @property
    @abstractmethod
    def id(self):
        """
        The id of the news-item
        """


class AtomContent(Content):
    """
    Implementation of Content for Atom feeds
    """

    @property
    def title(self):
        """
        The title of the news-item
        """
        try:
            title = self.item.find("{%s}title" % ATOM_URL)
            return title.text
        except Exception:
            return ""

    @title.setter
    def title(self, new_title):
        """
        Set the title of the news-item
        """
        try:
            title = self.item.find("{%s}title" % ATOM_URL)
            title.text = new_title
        except Exception:
            pass

    @property
    def description(self):
        """
        The description of the news-item
        """
        try:
            desc = self.item.find("{%s}summary" % ATOM_URL)
            return desc.text
        except Exception:
            return ""

    @description.setter
    def description(self, text):
        """
        Appends the given text to the description
        """
        try:
            desc = self.item.find("{%s}summary" % ATOM_URL)
            if desc is None:
                desc = etree.SubElement(self.item, "{%s}summary" % ATOM_URL)
            desc.text = text
        except Exception:
            pass

    @property
    def content(self):
        """
        The content of the news-item
        """
        try:
            cont = self.item.find("{%s}content" % ATOM_URL)
            return "".join([etree.tostring(i).decode() for i in list(cont)])
        except Exception:
            return ""

    @content.setter
    def content(self, text):
        """
        Appends the given text to the content
        """
        try:
            cont = self.item.find("{%s}content" % ATOM_URL)
            if cont is None:
                cont = etree.SubElement(self.item, "{%s}content" % ATOM_URL)
            try:
                new = etree.fromstring(text)
            except etree.ParseError:
                new = etree.fromstring("<div>" + text + "</div>")
            for i in list(cont):
                cont.remove(i)
            cont.append(new)
        except Exception:
            pass

    @property
    def link(self):
        """
        The link of the news-item
        """
        try:
            link = self.item.find("{%s}link" % ATOM_URL)
            return link.attrib["href"]
        except Exception:
            # This should never happen, handling necessary?
            return ""

    @property
    def id(self):
        """
        The id of the news-item
        """
        try:
            gid = self.item.find("{%s}id" % ATOM_URL)
            return gid.text
        except Exception:
            # This should never happen, handling necessary?
            return ""


class RSSContent(Content):
    """
    Implementation of Content for RSS feeds
    """

    @property
    def title(self):
        """
        The title of the news-item
        """
        try:
            title = self.item.find("title")
            return title.text.strip()
        except Exception:
            return ""

    @title.setter
    def title(self, new_title):
        """
        Set the title of the news-item
        """
        try:
            title = self.item.find("title")
            title.text = new_title
        except Exception:
            pass

    @property
    def description(self):
        """
        The description of the news-item
        """
        try:
            desc = self.item.find("description")
            return desc.text.strip()
        except Exception:
            return ""

    @description.setter
    def description(self, text):
        """
        Appends the given text to the description
        """
        try:
            desc = self.item.find("description")
            if desc is None:
                desc = etree.SubElement(self.item, "description")
            desc.text = text
        except Exception:
            pass

    @property
    def content(self):
        """
        The content of the news-item
        """
        try:
            cont = self.item.find("{%s}encoded" % RSS_URL)
            return cont.text.strip()
        except Exception:
            return ""

    @content.setter
    def content(self, text):
        """
        Appends the given text to the content
        """
        try:
            cont = self.item.find("{%s}encoded" % RSS_URL)
            if cont is None:
                cont = etree.SubElement(self.item, "{%s}encoded" % RSS_URL)
            cont.text = text
        except Exception:
            pass

    @property
    def link(self):
        """
        The link of the news-item
        """
        try:
            link = self.item.find("link")
            return link.text.strip()
        except Exception:
            # This should never happen, handling necessary?
            return ""

    @property
    def id(self):
        """
        The id of the news-item
        """
        try:
            gid = self.item.find("guid")
            return gid.text.strip()
        except Exception:
            # This should never happen, handling necessary?
            return ""


class Feed(ABC):
    """
    Parse and modify an Atom or RSS-Feed
    """

    child_iter: Iterator

    @property
    def Content_Type(self):
        raise NotImplementedError

    def __init__(self, tree):
        """
        Initiate the Feed
        """
        self.tree = tree
        self.root = self.tree.getroot()
        self.childen = OrderedDict()
        for rawchild in self._get_children_():
            child = self.Content_Type(rawchild)
            self.childen[child.id] = child

    def get_child(self, index):
        """
        Gets a child by its id
        """
        assert isinstance(index, str)
        return self.childen[index]

    @abstractmethod
    def _get_children_(self):
        """"""

    def __iter__(self):
        """
        Get all news-items in the feed
        """
        return iter(self.childen.values())

    @property
    @abstractmethod
    def lang(self):
        """
        The language of the feed
        """

    @abstractmethod
    def remove_item(self, child):
        """
        Remove an item from the feed
        """

    @abstractmethod
    def write(self, filename, encoding):
        """
        Write the feed to a file
        """

    def print(self):
        """
        Write the feed to stdout
        """
        self.write(sys.stdout, encoding="Unicode")


class AtomFeed(Feed):
    """
    Parse and modify an Atom Feed
    """

    Content_Type = AtomContent

    def _get_children_(self):
        return self.root.iterfind("{%s}entry" % ATOM_URL)

    @property
    def lang(self):
        """
        The language of the feed
        """
        try:
            return self.root.attrib["{%s}lang" % XML_URL].lower()
        except Exception:
            return ""

    def remove_item(self, child):
        """
        Remove an item from the feed
        """
        self.root.remove(child.item)

    def write(self, filename, encoding="UTF-8"):
        """
        Write the feed to a file
        """
        etree.register_namespace("", ATOM_URL)
        self.tree.write(filename, encoding=encoding, xml_declaration=True)


class RssFeed(Feed):
    """
    Parse and modify an RSS-Feed
    """

    Content_Type = RSSContent

    def _get_children_(self):
        return self.root.find("channel").iterfind("item")

    @property
    def lang(self):
        """
        The language of the feed
        """
        try:
            return self.root.find("channel").find("language").text.lower()
        except Exception:
            return ""

    def remove_item(self, child):
        """
        Remove an item from the feed
        """
        self.root.find("channel").remove(child.item)

    def write(self, filename, encoding="UTF-8"):
        """
        Write the feed to a file
        """
        self.tree.write(filename, encoding=encoding, xml_declaration=True)
