#!/usr/bin/env python3
import urllib.request
import sys
import os
import comparetext
from feed import Feed
import configparser
from filter import Filter
import utils
from utils import *


# parse arguments and read feed from file/url
if len(sys.argv) != 2:
    warn("no file/url given")
    exit(-1)
if sys.argv[1][0:4] == "http":
    feedfile = urllib.request.urlopen(sys.argv[1])
    sitename= sys.argv[1].split('.')[1]
else:
    feedfile = sys.argv[1]


# read env-variables
confdir = os.getenv('FEED_FILTER_CONF',
        os.path.join(os.getenv('HOME'), ".feedfilter"))
debug_mode = os.getenv('DEBUG',  "False")

# read configfile
configs = configparser.ConfigParser()
configs.read(os.path.join(confdir, 'feedfilter.conf'))
# default settings
treshhold = 1
cmp_treshhold = 0.35
title_scale = 2
appendlvl = False
utils.silent = True
outputfile = None
for section in ['DEFAULT', sitename]:
    if section in configs:
        config = configs[section]
    else:
        pass
    treshhold = float(config.get('treshhold', treshhold))
    cmp_treshhold = float(config.get('cmp_treshhold', cmp_treshhold))
    title_scale = float(config.get('title_scale', title_scale))
    appendlvl = toBool(config.get('appendlvl', appendlvl))
    utils.silent = toBool(config.get('silent', utils.silent))
    outputfile = config.get('outputfile', outputfile)
if debug_mode == "dev":
    utils.silent = False
    outputfile = 'output.xml'

# read and parse filterfiles
wordfilter = Filter(confdir)
wordfilter.read_filterlist('./blackwordlist.txt')
if 'sitename' in locals():
    wordfilter.read_filterlist(sitename)

# Parse feed
feed = Feed(feedfile)
lang = feed.get_lang()

wordlists={}
for child in feed.get_items(): 
    title = feed.get_title(child)
    summary = feed.get_description(child)
    content = feed.get_content(child)
    link = feed.get_link(child)
    gid = feed.get_id(child)

    lvl=0

    # Check for duplicates
    wordlist=comparetext.analyse(lang, title + " " + summary + " " + content )
    for index, dic in wordlists.items():
        t=comparetext.comp(wordlist, dic)
        if t>cmp_treshhold:
            feed.add_crosslink(index, link, title)
            warn("removing duplicate: ", title)
            warn("  is duplicate of: ", feed.get_title(index))
            lvl=treshhold+1
            continue
    if lvl > treshhold:
        feed.remove_item(child)
        continue
    else:
        wordlists[gid] = wordlist

    # Check against blackwords
    lvl  = wordfilter.check(title, title_scale)
    if content != "":
        lvl += wordfilter.check(content, 1)
    elif summary != "":
        lvl += wordfilter.check(summary, 1)
    if lvl > treshhold:
        warn("removing item!")
        feed.remove_item(child)
        del wordlists[gid]
    elif appendlvl:
        feed.append_description(child, "<br><br><small>lvl: " + str(lvl) + "</small>")
        if content != "":
            feed.append_content(child, "<br><br><small>lvl: " + str(lvl) + "</small>")
    log(lvl, title)

if outputfile == None:
    # Write output to console
    feed.print()
else:
    # Write output to file
    feed.write(outputfile)

