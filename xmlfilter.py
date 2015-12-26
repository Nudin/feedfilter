#!/usr/bin/env python3
import urllib.request
import sys
import os
import comparetext
from feed import Feed


def log(*objs):
    print("\033[0m", end="", flush=True)
    print(*objs, file=sys.stderr)
    print("\033[0m", end="", flush=True)

def warn(*objs):
    print("\033[31m", end="", flush=True)
    print(*objs, file=sys.stderr)
    print("\033[0m", end="", flush=True)

def read_filterlist(filename):
    blackwords = {}
    try:
        dir = os.path.dirname(__file__)
        with open(os.path.join(dir, filename), 'rU') as infile:
            for line in infile:
                tmp=line.strip().split('\t')
                blackwords[tmp[0]]=int(tmp[1])
    except IOError:
        warn('error opening file:', filename)
    return blackwords


treshhold = 1
title_scale = 2


# parse arguments and read feed from file/url
if len(sys.argv) != 2:
    warn("no file/url given")
    exit(-1)
if sys.argv[1][0:4] == "http":
    feedfile = urllib.request.urlopen(sys.argv[1])
    sitename= sys.argv[1].split('.')[1]
else:
    feedfile = sys.argv[1]

# read backwordlist
blackwords = read_filterlist('./blackwordlist.txt')
blackwords = read_filterlist(sitename)


wordlists=[]

feed = Feed(feedfile)
for child in feed.get_items(): 
    title = feed.get_title(child)
    summary = feed.get_description(child)
    content = feed.get_content(child)
    link = feed.get_link(child)

    lvl=0

    wordlist=comparetext.analyse(title + " " + summary + " " + content )
    for index, dic in enumerate(wordlists):
        t=comparetext.comp(wordlist, dic)
        if t>0.5:
            feed.append_description(index, "<br><br>Siehe auch: <a href=\"" + link + "\">"+title+"</a>")
            warn("removing dupplicate: ", title)
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
        warn("removing item!")
        feed.remove_item(child)
    log(lvl, title)


# Write output to console
#feed.print()
# Write output to file
feed.write('output.xml')

