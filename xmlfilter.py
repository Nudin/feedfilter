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

# Load feed, detect format and get root
tree = etree.parse(feedfile)
root = tree.getroot()
if root.tag == '{http://www.w3.org/2005/Atom}feed':
    spec='http://www.w3.org/2005/Atom'
    channel_spec=None
    item_spec='{' + spec + '}entry'
    title_spec='{' + spec + '}title'
    link_spec='{' + spec + '}link'
    description_spec='{' + spec + '}summary'
elif root.tag == 'rss':
    spec=None
    channel='channel'
    item_spec='item'
    title_spec='title'
    link_spec='link'
    description_spec='description'
    root=root.find(channel)
else:
    print("Unknown feedformat!")
    exit

wordlists=[]

items = root.findall(item_spec)
for child in items: 
    title = child.find(title_spec).text
    summary = child.find(description_spec).text # Todo: test for null
    link = child.find(link_spec).attrib['href'] # Todo: fix for RSS (text)
    # Todo: use content if available

    lvl=0

    wordlist=comparetext.analyse(title + " " + summary)
    for index, dic in enumerate(wordlists):
        t=comparetext.comp(wordlist, dic)
        if t>0.5:
            items[index].find(description_spec).text += "<br>Siehe auch: <a href=\"" + link + "\">"+title+"</a>"
            root.remove(child)
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
        root.remove(child)
    print(lvl, title)

for item in root.findall(item_spec):
    title = item.find(description_spec).text
    #print(title)


etree.register_namespace('',spec)
# Write output to console
#tree.write(1, encoding="UTF-8", xml_declaration=True)
# Write output to file
tree.write('output.xml', encoding="UTF-8", xml_declaration=True)

