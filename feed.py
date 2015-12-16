import xml.etree.ElementTree as etree

class Feed():
    def __init__(self, feedfile):
        self.tree = etree.parse(feedfile)
        self.root = self.tree.getroot()
        if self.root.tag == '{http://www.w3.org/2005/Atom}feed':
            self.format = 'atom'
        elif self.root.tag == 'rss':
            self.format = 'rss'
        else:
            print("Unknown feedformat!")
            exit
       
    def __index2child(self, indexorchild):
        if type(indexorchild) is int:
            return self.get_items()[indexorchild]
        else:
            return indexorchild

    def get_items(self):
        if self.format == 'atom':
            return self.root.findall('{http://www.w3.org/2005/Atom}entry')
        elif self.format == 'rss':
            return self.root.find('channel').findall('item')

    def get_title(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            title = child.find('{http://www.w3.org/2005/Atom}title')
            if title != None:
                return title.text
        elif self.format == 'rss':
            title = child.find('title')
            if title != None:
                return title.text
        return ""

    def get_description(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            desc = child.find('{http://www.w3.org/2005/Atom}summary')
            if desc != None:
                return desc.text 
        elif self.format == 'rss':
            desc = child.find('description')
            if desc != None:
                return desc.text
        return ""

    def append_description(self, indexorchild, text):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            desc = child.find('{http://www.w3.org/2005/Atom}summary')
            if desc != None:
                desc.text += text   # todo: create if not existing
        elif self.format == 'rss':
            desc = child.find('description')
            if desc != None:
                desc.text += text   # todo: create if not existing

    def get_link(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            link = child.find('{http://www.w3.org/2005/Atom}link')
            if link != None:
                return link.attrib['href']
        elif self.format == 'rss':
            link =  child.find('link')
            if link != None:
                return link.text

    def remove_item(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            self.root.remove(child)
        elif self.format == 'rss':
            self.root.find('channel').remove(child)

    def write(self, filename):
        if self.format == 'atom':
           etree.register_namespace('', 'http://www.w3.org/2005/Atom')
        self.tree.write(filename, encoding="UTF-8", xml_declaration=True)

    def print(self):
        self.write(1)

