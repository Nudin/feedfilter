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
import sys
import xml.etree.ElementTree as etree
from abc import ABC, abstractmethod
from collections import OrderedDict

from bs4 import BeautifulSoup

RSS_URL = "http://purl.org/rss/1.0/modules/content/"
ATOM_URL = "http://www.w3.org/2005/Atom"
XML_URL = "http://www.w3.org/XML/1998/namespace"


def get_feed(feed_file):
    """
    Determine the format of the feed and parse it
    """
    tree = etree.parse(feed_file)
    root = tree.getroot()
    if root.tag == "{%s}feed" % ATOM_URL:
        return AtomFeed(tree)
    if root.tag == "rss":
        return RssFeed(tree)
    raise NotImplementedError("Unknown feedformat!")


class Content(ABC):
    @abstractmethod
    def __init__(self, content):
        pass

    @abstractmethod
    def append_links(self, links):
        pass

    @abstractmethod
    def append_stats(self, lvl, threshold, maxsim):
        pass


class TextContent(Content):
    def __init__(self, content):
        super().__init__(content)
        self.content = content

    def append_links(self, links):
        if len(links) > 0:
            self.content += "\n"
        for item in links:
            self.content += "\n{}- ".format(item.title)

    def append_stats(self, lvl, threshold, maxsim):
        self.content += "\n\nlvl: %.2g/%g &nbsp;maxcmplvl: %.2f" % (
            lvl,
            threshold,
            maxsim,
        )

    def __str__(self):
        return self.content


class HTMLContent(Content):
    def __init__(self, content):
        super().__init__(content)
        self.content = BeautifulSoup(content, "html.parser")

    def append_links(self, links):
        body = self.content.find("body") or self.content
        ulist = self.content.new_tag("ul")
        body.append(ulist)
        for item in links:
            link = self.content.new_tag("a")
            link.atrrs["href"] = item.link
            link.string = item.title
            li = self.content.new_tag("li")
            ulist.append(li)
            li.append(link)

    def append_stats(self, lvl, threshold, maxsim):
        body = self.content.find("body") or self.content
        container = self.content.new_tag("small")
        container.string = "lvl: %.2g/%g &nbsp;maxcmplvl: %.2f" % (
            lvl,
            threshold,
            maxsim,
        )
        body.append(self.content.new_tag("br"))
        body.append(container)

    def __str__(self):
        return str(self.content)


class FeedItem(ABC):
    """
    Represents one item of a feed.
    """

    merged_items = []

    # The title of the news-item
    title: str
    # The description of the news-item
    description: Content
    # The content of the news-item
    content: Content
    # The link of the news-item
    link: str
    # The id of the news-item
    id: str

    lvl = 0
    threshold = None
    maxsim = 0

    def __init__(self, item):
        self.data = item

    def merge_item(self, item):
        self.merged_items.append(item)

    def append_crosslinks(self):
        """
        Append the given link to the description and content under an heading "see also"
        """
        if len(self.merged_items) == 0:
            return

        self.description.append_links(self.merged_items)
        self.content.append_links(self.merged_items)
        self.title = self.title + "[+%i]" % len(self.merged_items)

    def sync(self):
        self.append_crosslinks()
        self.append_stats()

    def set_stats(self, lvl, threshold, maxsim):
        self.lvl = lvl
        self.threshold = threshold
        self.maxsim = maxsim

    def append_stats(self):
        self.description.append_stats(self.lvl, self.threshold, self.maxsim)
        self.content.append_stats(self.lvl, self.threshold, self.maxsim)


class XMLFeedItem(FeedItem):
    """
    Represents one item of a XML based feed.
    """

    def _find_or_create_(self, tag_name, search_in=None):
        """
        Search a tag of type `tag_name` and create if not existing.

        Will search in `search_in` or in self.item is not provided. Finds only
        direct child entities.
        """
        search_in = search_in or self.data
        element = search_in.find(tag_name)
        if element is None:
            element = etree.SubElement(search_in, tag_name)
        return element

    def _get_text_(self, element_name):
        """
        Get the text content of an element with given name
        """
        try:
            element = self.data.find(element_name)
            return element.text.strip()
        except Exception:
            return ""

    def _set_text_(self, element_name, text):
        """
        Set the text content of an element with given name
        """
        try:
            element = self._find_or_create_(element_name)
            element.text = text
        except Exception:
            pass


class AtomFeedItem(XMLFeedItem):
    """
    Implementation of Content for Atom feeds
    """

    # implementation = {
    #     "title": "{%s}title" % ATOM_URL,
    #     "description": "{%s}summary" % ATOM_URL,
    # }

    def __init__(self, src):
        super().__init__(src)
        self.item = src
        self.parse()

    def parse(self):
        self.id = self.get_id()
        self.title = self.get_title()
        self.link = self.get_link()
        self.description = self.get_description()
        self.content = self.get_content()

    def sync(self):
        super().sync()
        # self.set_id(self.id)
        self.set_title(self.title)
        # self.set_link(self.link)
        self.set_description(self.description)
        self.set_content(self.content)

    def get_title(self):
        """ The title of the news-item """
        return self._get_text_("{%s}title" % ATOM_URL)

    def set_title(self, text):
        """ Set the title of the news-item """
        self._set_text_("{%s}title" % ATOM_URL, text)

    def get_description(self):
        """ The description of the news-item """
        ctype = self.data.find("{%s}summary" % ATOM_URL).attrib["type"]
        content = self._get_text_("{%s}summary" % ATOM_URL)
        if ctype == "html":
            return HTMLContent(content)
        else:
            return TextContent(content)

    def set_description(self, content):
        """ Set the description """
        self._set_text_("{%s}summary" % ATOM_URL, str(content))

    def get_content(self):
        """ The content of the news-item """
        ctype = self.data.find("{%s}content" % ATOM_URL).attrib["type"]
        content = self._get_text_("{%s}content" % ATOM_URL)
        if ctype == "html":
            return HTMLContent(content)
        else:
            return TextContent(content)

    def set_content(self, content):
        """ Set the content """
        self._set_text_("{%s}content" % ATOM_URL, str(content))

    def get_link(self):
        """ The link of the news-item """
        try:
            link = self.item.find("{%s}link" % ATOM_URL)
            return link.attrib["href"]
        except Exception:
            # This should never happen, handling necessary?
            return ""

    def get_id(self):
        """ The id of the news-item """
        return self._get_text_("{%s}id" % ATOM_URL)


class RSSFeedItem(XMLFeedItem):
    """
    Implementation of Content for RSS feeds
    """

    def __init__(self, src):
        super().__init__(src)
        self.item = src
        self.parse()

    def parse(self):
        self.id = self.get_id()
        self.title = self.get_title()
        self.link = self.get_link()
        self.description = self.get_description()
        self.content = self.get_content()

    def sync(self):
        # self.set_id(self.id)
        self.set_title(self.title)
        # self.set_link(self.link)
        self.set_description(self.description)
        self.set_content(self.content)

    def get_title(self):
        """ The title of the news-item """
        return self._get_text_("title")

    def set_title(self, text):
        """ Set the title of the news-item """
        self._set_text_("title", text)

    def get_description(self):
        """ The description of the news-item """
        return HTMLContent(self._get_text_("description"))

    def set_description(self, content):
        """ Set the description """
        self._set_text_("description", str(content))

    def get_content(self):
        """ The content of the news-item """
        return HTMLContent(self._get_text_("{%s}encoded" % RSS_URL))

    def set_content(self, content):
        """ Set the content """
        self._set_text_("{%s}encoded" % RSS_URL, str(content))

    def get_link(self):
        """ The link of the news-item """
        return self._get_text_("link")

    def get_id(self):
        """ The id of the news-item """
        return self._get_text_("guid")


class Feed(ABC):
    """
    Parse and modify an Atom or RSS-Feed
    """

    @property
    def Content_Type(self):
        raise NotImplementedError

    def __init__(self):
        """
        Initiate the Feed
        """
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

    def sync(self):
        """
        Update the data representation
        """
        for child in self.childen:
            child.sync()

    @abstractmethod
    def write(self, filename, encoding):
        """
        Write the feed to a file
        """
        self.sync()

    def print(self):
        """
        Write the feed to stdout
        """
        self.write(sys.stdout, encoding="Unicode")


class XMLFeed(Feed):
    def __init__(self, tree):
        """
        Initiate the Feed
        """
        self.tree = tree
        self.root = self.tree.getroot()
        super().__init__()


class AtomFeed(XMLFeed):
    """
    Parse and modify an Atom Feed
    """

    Content_Type = AtomFeedItem

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
        super().write(filename, encoding)
        etree.register_namespace("", ATOM_URL)
        self.tree.write(filename, encoding=encoding, xml_declaration=True)


class RssFeed(XMLFeed):
    """
    Parse and modify an RSS-Feed
    """

    Content_Type = RSSFeedItem

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
        super().write(filename, encoding)
        self.tree.write(filename, encoding=encoding, xml_declaration=True)
