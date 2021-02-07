import xml.etree.ElementTree as etree

from .content import HTMLContent, NoContent, TextContent
from .xml import XMLFeed, XMLFeedItem

ATOM_URL = "http://www.w3.org/2005/Atom"
XML_URL = "http://www.w3.org/XML/1998/namespace"


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
        self.categories = self.get_categories()

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
        element = self.data.find("{%s}summary" % ATOM_URL)
        if element is None:
            return NoContent()
        ctype = element.attrib.get("type", "text")
        content = self._get_text_("{%s}summary" % ATOM_URL)
        if ctype == "html":
            return HTMLContent(content)
        else:
            return TextContent(content)

    def set_description(self, content):
        """ Set the description """
        if not isinstance(content, NoContent):
            self._set_text_("{%s}summary" % ATOM_URL, str(content))

    def get_content(self):
        """ The content of the news-item """
        element = self.data.find("{%s}content" % ATOM_URL)
        if element is None:
            return NoContent()
        ctype = element.attrib.get("type", "text")
        content = self._get_text_("{%s}content" % ATOM_URL)
        if ctype == "html":
            return HTMLContent(content)
        else:
            return TextContent(content)

    def set_content(self, content):
        """ Set the content """
        if not isinstance(content, NoContent):
            self._set_text_("{%s}content" % ATOM_URL, str(content))

    def get_categories(self):
        """ The categories of the news-item """
        return self._get_text_("{%s}category" % ATOM_URL)

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
        super().remove_item(child)
        self.root.remove(child.item)

    def write(self, filename, encoding="UTF-8"):
        """
        Write the feed to a file
        """
        super().write(filename, encoding)
        etree.register_namespace("", ATOM_URL)
        self.tree.write(filename, encoding=encoding, xml_declaration=True)
