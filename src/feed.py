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
import string
import random
import re
import xml.etree.ElementTree as etree
from gettext import gettext as _


class Feed():
    """
    Parse and modify an Atom or RSS-Feed
    """
    atom_url = 'http://www.w3.org/2005/Atom'
    rss_url = 'http://purl.org/rss/1.0/modules/content/'
    xml_rul = 'https://www.w3.org/XML/1998/namespace'

    def __init__(self, feedfile):
        """
        Initiate the Feed

        feedfile: filename or context manager of the feed
        """
        self.tree = etree.parse(feedfile)
        self.root = self.tree.getroot()
        if self.root.tag == '{%s}feed' % self.atom_url:
            self.format = 'atom'
        elif self.root.tag == 'rss':
            self.format = 'rss'
        else:
            print(_("Unknown feedformat!"))
            exit
        randomstr = ''.join(random.choice(string.ascii_letters) for _ in range(12))
        self.marker = "<!--" + randomstr + "-->"

    def __get_child(self, idindexorchild):
        """
        Gets a child by an identifier
        the identifier can be:
            * the child itself (in this case the function will simply return it)
            * the index-number (deprecated)
            * the id of the child
        """
        if type(idindexorchild) is int:
            return list(self)[idindexorchild]
        elif type(idindexorchild) is str:
            for child in self:
                if self.get_id(child) == idindexorchild:
                    return child
        else:
            return idindexorchild

    def __iter__(self):
        """
        Get all news-items in the feed
        """
        if self.format == 'atom':
            return iter(self.root.findall('{%s}entry' % self.atom_url))
        elif self.format == 'rss':
            return iter(self.root.find('channel').findall('item'))

    def get_lang(self):
        """
        Get the language of the feed
        """
        try:
            if self.format == 'atom':
                return self.root.attrib['{%s}lang' % self.xml_url].lower()
            elif self.format == 'rss':
                return self.root.find('channel').find('language').text.lower()
        except Exception:
            return ""


    def get_title(self, idindexorchild):
        """
        Get the title of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                title = child.find('{%s}title' % self.atom_url)
                return title.text
            elif self.format == 'rss':
                title = child.find('title')
                return title.text.strip()
        except Exception:
            return ""

    def set_title(self, idindexorchild, newtitle):
        """
        Set the title of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                title = child.find('{%s}title' % self.atom_url)
                title.text = newtitle
            elif self.format == 'rss':
                title = child.find('title')
                title.text = newtitle
        except Exception:
            pass

    def get_description(self, idindexorchild):
        """
        Get the description of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                desc = child.find('{%s}summary' % self.atom_url)
                return desc.text
            elif self.format == 'rss':
                desc = child.find('description')
                return desc.text.strip()
        except Exception:
            return ""

    def set_description(self, idindexorchild, text):
        """
        Appends the given text to the description
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                desc = child.find('{%s}summary' % self.atom_url)
                if desc is None:
                    desc = etree.SubElement(child, '{%s}summary' % self.atom_url)
                desc.text = text
            elif self.format == 'rss':
                desc = child.find('description')
                if desc is None:
                    desc = etree.SubElement(child, 'description')
                desc.text = text
        except Exception:
            pass

    def append_description(self, idindexorchild, text):
        """
        Appends the given text to the description
        """
        self.set_description(idindexorchild,
                             self.get_description(idindexorchild) + text)

    def _insert_or_append(self, text, addition):
        p = text.find(self.marker)
        if p == -1:
            text += _("<br>Similar News:<ul><li>%(link)s</li>%(marker)s</ul>") % \
                      {'link': addition, 'marker': self.marker}
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
            self.set_content(idindexorchild, self._insert_or_append(cont, fulllink))
        title = self.get_title(idindexorchild)
        if re.match('\[\+\d\]', title[-4:]):
            num = int(title[-2]) + 1 
            self.set_title(idindexorchild, title[:-4] + '[+%i]' % num)
        else:
            self.set_title(idindexorchild, title + ' [+1]')

    def get_content(self, idindexorchild):
        """
        Get the content of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                cont = child.find('{%s}content' % self.atom_url)
                return ''.join([etree.tostring(i).decode() for i in list(cont)])
            elif self.format == 'rss':
                cont = child.find('{%s}encoded' % self.rss_url)
                return cont.text.strip()
        except Exception:
            return ""

    def set_content(self, idindexorchild, text):
        """
        Appends the given text to the content
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                cont = child.find('{%s}content' % self.atom_url)
                if cont is None:
                    cont = etree.SubElement(child, '{%s}content' % self.atom_url)
                try:
                        new = etree.fromstring(text)
                except etree.ParseError:
                        new = etree.fromstring('<div>' + text + '</div>')
                [cont.remove(i) for i in list(cont)]
                cont.append(new)
            elif self.format == 'rss':
                cont = child.find('{%s}encoded' % self.rss_url)
                if cont is None:
                    cont = etree.SubElement(child, '{%s}encoded' % self.rss_url)
                cont.text = text
        except Exception:
            pass

    def append_content(self, idindexorchild, text):
        """
        Appends the given text to the content
        """
        self.set_content(idindexorchild, self.get_content(idindexorchild) + text)

    def get_link(self, idindexorchild):
        """
        Get the link of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                link = child.find('{%s}link' % self.atom_url)
                return link.attrib['href']
            elif self.format == 'rss':
                link = child.find('link')
                return link.text.strip()
        except Exception:
            # This should never happen, handling necessary?
            return ""

    def get_id(self, idindexorchild):
        """
        Get the id of a news-item
        """
        try:
            child = self.__get_child(idindexorchild)
            if self.format == 'atom':
                gid = child.find('{%s}id' % self.atom_url)
                return gid.text
            elif self.format == 'rss':
                gid = child.find('guid')
                return gid.text.strip()
        except Exception:
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
            etree.register_namespace('', self.atom_url)
        self.tree.write(filename, encoding="UTF-8", xml_declaration=True)

    def print(self):
        """
        Write the feed to stdout
        """
        self.write(1)
