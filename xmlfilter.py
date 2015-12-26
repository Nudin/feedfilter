#!/usr/bin/env python3
import urllib.request
import sys
import os
import comparetext
from feed import Feed

def log(*objs):
    print(*objs, file=sys.stderr)

treshhold = 1
title_scale = 2

# read backwordlist
blackwords = {}
try:
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir,'./blackwordlist.txt'), 'rU') as infile:
        for line in infile:
        	tmp=line.strip().split('\t')
        	blackwords[tmp[0]]=int(tmp[1])
except IOError:
       print('error opening file')

if sys.argv[1][0:4] == "http":
    feedfile = urllib.request.urlopen(sys.argv[1])
else:
    feedfile = sys.argv[1]


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
            feed.append_description(index, "<br><br>Siehe auch: <a href=\"" + link + "\">"+title+"</a>")
            log("removing dupplicate: ", title)
            feed.remove_item(child)
            lvl=treshhold+1
            continue
    if lvl > treshhold:
        continue
    else:
        wordlists.append(wordlist)
    
    for word in blackwords:
        if title.find(word) != -1:
        	lvl += title_scale*blackwords[word]
    for word in blackwords:
        if summary.find(word) != -1:
        	lvl += blackwords[word]
    if lvl > treshhold:
        log("removing item!")
        feed.remove_item(child)
    log(lvl, title)


# Write output to console
#feed.print()
# Write output to file
feed.write('output.xml')

