import xml.etree.ElementTree as etree

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


# Load feed and parse it
tree = etree.parse('feed.xml')
root = tree.getroot()

for child in root.findall('{http://www.w3.org/2005/Atom}entry'): 
    title = child.find('{http://www.w3.org/2005/Atom}title').text
    summary = child.find('{http://www.w3.org/2005/Atom}summary').text
    
    lvl=0
    for word in blackwords:
        if title.find(word) != -1:
        	lvl += title_scale*blackwords[word]
    for word in blackwords:
        if summary.find(word) != -1:
        	lvl += blackwords[word]
    if lvl > treshhold:
        root.remove(child)
    #print(lvl, title)

etree.register_namespace('',"http://www.w3.org/2005/Atom")
#tree.write(1, encoding="UTF-8", xml_declaration=True)
tree.write('output.xml', encoding="UTF-8", xml_declaration=True)

