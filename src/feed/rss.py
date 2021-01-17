from .content import HTMLContent, TextContent
from .xml import XMLFeed, XMLFeedItem

RSS_URL = "http://purl.org/rss/1.0/modules/content/"


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
        super().sync()
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
        super().remove_item(child)
        self.root.find("channel").remove(child.item)

    def write(self, filename, encoding="UTF-8"):
        """
        Write the feed to a file
        """
        super().write(filename, encoding)
        self.tree.write(filename, encoding=encoding, xml_declaration=True)
