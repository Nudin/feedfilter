import xml.etree.ElementTree as etree

from .feed import Feed, FeedItem


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


class XMLFeed(Feed):
    def __init__(self, tree):
        """
        Initiate the Feed
        """
        self.tree = tree
        self.root = self.tree.getroot()
        super().__init__()
