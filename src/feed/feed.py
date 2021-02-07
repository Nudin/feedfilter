import sys
from abc import ABC, abstractmethod
from collections import OrderedDict

from .content import Content


class FeedItem(ABC):
    """
    Represents one item of a feed.
    """

    merged_items = None

    # The title of the news-item
    title: str
    # The description of the news-item
    description: Content
    # The content of the news-item
    content: Content
    # The categories of the news-item
    categories: Content
    # The link of the news-item
    link: str
    # The id of the news-item
    id: str

    append_stats = False
    deleted = False
    lvl = -1
    threshold = -1
    maxsim = -1

    def __init__(self, item):
        self.data = item
        self.merged_items = []

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
        self.title = self.title + " [+%i]" % len(self.merged_items)

    def sync(self):
        if not self.deleted:
            self.append_crosslinks()
            self._append_stats()

    def set_stats(self, lvl, threshold, maxsim):
        self.lvl = lvl
        self.threshold = threshold
        self.maxsim = maxsim

    def _append_stats(self):
        if self.append_stats:
            self.description.append_stats(self.lvl, self.threshold, self.maxsim)
            self.content.append_stats(self.lvl, self.threshold, self.maxsim)


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
        self.childen[child.id].deleted = True

    def sync(self):
        """
        Update the data representation
        """
        for child in self.childen.values():
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
