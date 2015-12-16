import xml.etree.ElementTree as etree
import urllib.request
import sys
import comparetext

treshhold = 1
title_scale = 2

# read backwordlist
blackwords = {}
try:
    with open('blackwordlist.txt', 'rU') as infile:
        for line in infile:
        	tmp=line.strip().split('\t')
        	blackwords[tmp[0]]=int(tmp[1])
except IOError:
       print('error opening file')

if sys.argv[1][0:4] == "http":
    feedfile = urllib.request.urlopen(sys.argv[1])
else:
    feedfile = sys.argv[1]


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
            return child.find('{http://www.w3.org/2005/Atom}title').text    # todo: check for null
        elif self.format == 'rss':
            return child.find('title').text

    def get_description(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            return child.find('{http://www.w3.org/2005/Atom}summary').text  # todo: check for null
        elif self.format == 'rss':
            return child.find('description').text

    def append_description(self, indexorchild, text):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            child.find('{http://www.w3.org/2005/Atom}summary').text += text # todo: check for null
        elif self.format == 'rss':
            child.find('description').text += text

    def get_link(self, indexorchild):
        child = self.__index2child(indexorchild)
        if self.format == 'atom':
            return child.find('{http://www.w3.org/2005/Atom}link').attrib['href']   # todo: check for null
        elif self.format == 'rss':
            return child.find('link').text

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



wordlists=[]

feed = Feed(feedfile)
for child in feed.get_items(): 
    title = feed.get_title(child)
    summary = feed.get_description(child)
    link = feed.get_link(child)
    # Todo: use content if available

    lvl=0

    wordlist=comparetext.analyse(title + " " + summary)
    for index, dic in enumerate(wordlists):
        t=comparetext.comp(wordlist, dic)
        if t>0.5:
            feed.append_description(index, "<br>Siehe auch: <a href=\"" + link + "\">"+title+"</a>")
            print("removing dupplicate!")
            feed.remove_item(child)
            continue
    wordlists.append(wordlist)
    
    for word in blackwords:
        if title.find(word) != -1:
        	lvl += title_scale*blackwords[word]
    for word in blackwords:
        if summary.find(word) != -1:
        	lvl += blackwords[word]
    if lvl > treshhold:
        print("removing item!")
        feed.remove_item(child)
    print(lvl, title)


# Write output to console
#feed.print()
# Write output to file
feed.write('output.xml')

