import xml.etree.ElementTree as etree
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

# Load feed, detect format and get root
tree = etree.parse(sys.argv[1])
root = tree.getroot()
if root.tag == '{http://www.w3.org/2005/Atom}feed':
    spec='http://www.w3.org/2005/Atom'
    channel_spec=None
    item_spec='{' + spec + '}entry'
    title_spec='{' + spec + '}title'
    description_spec='{' + spec + '}summary'
elif root.tag == 'rss':
    spec=None
    channel='channel'
    item_spec='item'
    title_spec='title'
    description_spec='description'
    root=root.find(channel)
else:
    print("Unknown feedformat!")
    exit

wordlists=[]

for child in root.findall(item_spec): 
    title = child.find(title_spec).text
    summary = child.find(description_spec).text

    lvl=0

    wordlist=comparetext.analyse(title + " " + summary)
    for dic in wordlists:
        t=comparetext.comp(wordlist, dic)
        if t>lvl:
            lvl=t
    wordlists.append(wordlist)

    lvl *= 1.5 * treshhold
    
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

etree.register_namespace('',spec)
# Write output to console
#tree.write(1, encoding="UTF-8", xml_declaration=True)
# Write output to file
#tree.write('output.xml', encoding="UTF-8", xml_declaration=True)

