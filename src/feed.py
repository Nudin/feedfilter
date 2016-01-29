import string
import random
import xml.etree.ElementTree as etree


class Feed():
    """
    Parse and modify an Atom or RSS-Feed
    """

    def __init__(self, feedfile):
        """
        Initiate the Feed

        feedfile: filename or context manager of the feed
        """
        self.tree = etree.parse(feedfile)
        self.root = self.tree.getroot()
        if self.root.tag == '{http://www.w3.org/2005/Atom}feed':
            self.format = 'atom'
        elif self.root.tag == 'rss':
            self.format = 'rss'
        else:
            print("Unknown feedformat!")
            exit
        self.marker = "<!--" + ''.join(random.choice(string.ascii_letters) for _ in range(12)) + "-->"
       
    def __get_child(self, idindexorchild):
        """
        Gets a child by an identifier
        the identifier can be:
            * the child itself (in this case the function will simply return it)
            * the index-number (deprecated)
            * the id of the child
        """
        if type(idindexorchild) is int:
            return self.get_items()[idindexorchild]
        elif type(idindexorchild) is str:
            for child in self.get_items():
                if self.get_id(child) == idindexorchild:
                    return child
        else:
            return idindexorchild

    def get_items(self):
        """
        Get all news-items in the feed
        returns an array
        """
        if self.format == 'atom':
            return self.root.findall('{http://www.w3.org/2005/Atom}entry')
        elif self.format == 'rss':
            return self.root.find('channel').findall('item')

    def get_lang(self):
        """
        Get the language of the feed
        """
        if self.format == 'atom':
            return self.root.attrib['{http://www.w3.org/XML/1998/namespace}lang'].lower()
        elif self.format == 'rss':
            return self.root.find('channel').find('language').text.lower()

    def get_title(self, idindexorchild):
        """
        Get the title of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                title = child.find('{http://www.w3.org/2005/Atom}title')
                return title.text
            elif self.format == 'rss':
                title = child.find('title')
                return title.text
        except (AttributeError):
            return ""

    def get_description(self, idindexorchild):
        """
        Get the description of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                desc = child.find('{http://www.w3.org/2005/Atom}summary')
                return desc.text 
            elif self.format == 'rss':
                desc = child.find('description')
                return desc.text
        except (AttributeError):
            return ""


    def set_description(self, idindexorchild, text):
        """
        Appends the given text to the description
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                desc = child.find('{http://www.w3.org/2005/Atom}summary')
                if desc is None:
                    desc = etree.SubElement(child, '{http://www.w3.org/2005/Atom}summary')
                desc.text = text
            elif self.format == 'rss':
                desc = child.find('description')
                if desc is None:
                    desc = etree.SubElement(child, 'description')
                desc.text = text
        except (AttributeError):
            pass


    def append_description(self, idindexorchild, text):
        """
        Appends the given text to the description
        """
        self.set_description(idindexorchild, self.get_description(idindexorchild) + text)

    def _insert_or_append(self, text, addition):
        p=text.find(self.marker)
        if p == -1:
            text += "<br>Siehe auch:<ul><li>" + addition + "</li>" + self.marker + "<ul>"
        else:
            text = text[0:p] + "<li>" + addition + "</li>" + text[p:]
        return text


    def add_crosslink(self, idindexorchild, link, title):
        """
        Appends the given link to the description and content under an heading "see also"
        """
        fulllink = "<a href=\"" + link + "\">" + title + "</a>"
        desc = self.get_description(idindexorchild)
        if desc != "":
            self.set_description(idindexorchild, self._insert_or_append(desc, fulllink))

        cont = self.get_content(idindexorchild)
        if cont != "":
            self.set_content(idindexorchild, self._insert_or_append(cont, fulllink ))


    def get_content(self, idindexorchild):
        """
        Get the content of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                cont = child.find('{http://www.w3.org/2005/Atom}content')
                return ''.join([etree.tostring(i).decode() for i in list(cont)])
            elif self.format == 'rss':
                cont = child.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                return cont.text
        except (AttributeError):
            return ""


    def set_content(self, idindexorchild, text):
        """
        Appends the given text to the content
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                cont = child.find('{http://www.w3.org/2005/Atom}content')
                if cont is None:
                    cont = etree.SubElement(child, '{http://www.w3.org/2005/Atom}content')
                try:
                        new = etree.fromstring(text)
                except etree.ParseError:
                        new = etree.fromstring('<div>' + text + '</div>')
                [c.remove(i) for i in list(c)]
                c.append(new)
            elif self.format == 'rss':
                cont = child.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                if cont is None:
                    cont = etree.SubElement(child, '{http://purl.org/rss/1.0/modules/content/}encoded')
                cont.text = text
        except (AttributeError):
            pass

    def append_content(self, idindexorchild, text):
        """
        Appends the given text to the content
        """
        self.set_conent(idindexorchild, self.get_content(idindexorchild) + text)

    def get_link(self, idindexorchild):
        """
        Get the link of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                link = child.find('{http://www.w3.org/2005/Atom}link')
                return link.attrib['href']
            elif self.format == 'rss':
                link =  child.find('link')
                return link.text
        except (AttributeError):
            # This should never happen, handling necessary? 
            return ""

    def get_id(self, idindexorchild):
        """
        Get the id of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                gid = child.find('{http://www.w3.org/2005/Atom}id')
                return gid.text
            elif self.format == 'rss':
                gid =  child.find('guid')
                return gid.text
        except (AttributeError):
            # This should never happen, handling necessary? 
            return ""

    def remove_item(self, idindexorchild):
        """
        Remove an item from the feed
        """
        child = self.__get_child(idindexorchild)
        if self.format == 'atom':
            self.root.remove(child)
        elif self.format == 'rss':
            self.root.find('channel').remove(child)

    def write(self, filename):
        """
        Write the feed to a file
        """
        if self.format == 'atom':
           etree.register_namespace('', 'http://www.w3.org/2005/Atom')
        self.tree.write(filename, encoding="UTF-8", xml_declaration=True)

    def print(self):
        """
        Write the feed to stdout
        """
        self.write(1)

