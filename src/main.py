#!/usr/bin/env python3
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
import gettext
from gettext import gettext as _
import sys
import urllib.request

import comparetext
from feed import Feed
from filter import Filter
import logging
import settings
import utils

# setup gettext
gettext.textdomain('feedfilter')

# parse arguments and read feed from file/url
if len(sys.argv) != 2:
    logging.warn(_("no file/url given"))
    exit(-1)
url = sys.argv[1]
if url[0:4] == "http":
    feedfile = urllib.request.urlopen(url)
else:
    feedfile = url

settings.read_settings(url)

utils.setupLogger()

# read and parse filterfiles
wordfilter = Filter()
wordfilter.read_filterlist('./blackwordlist.txt')
wordfilter.read_filterlist(settings.sitename)

# Parse feed
feed = Feed(feedfile)
# For now we use the language without any regional variants
lang = feed.get_lang().split('-')[0]

wordlists = {}
for child in feed:
    title = feed.get_title(child)
    summary = feed.get_description(child)
    content = feed.get_content(child)
    link = feed.get_link(child)
    gid = feed.get_id(child)

    # Check for duplicates
    maxcmplvl = 0
    wordlist = comparetext.analyse(lang, title, summary, content)
    for index, dic in wordlists.items():
        t = comparetext.comp(wordlist, dic)
        maxcmplvl = max(maxcmplvl, t)
        if t > settings.cmp_threshold:
            feed.add_crosslink(index, link, title)
            logging.warn(_("removing news entry: %(duplicate)s\n\tas duplicate of: %(news)s") %
                         {'duplicate': title, 'news': feed.get_title(index)})
            continue
    if maxcmplvl > settings.cmp_threshold:
        feed.remove_item(child)
        continue
    else:
        wordlists[gid] = wordlist

    # Check against blackwords
    lvl = wordfilter.check(title, settings.title_scale)
    if content != "":
        lvl += wordfilter.check(content, 1)
    elif summary != "":
        lvl += wordfilter.check(summary, 1)
    if lvl > settings.threshold:
        logging.warn(_("removing item %(title)s with score %(score)i") %
                     {'title': title, 'score': lvl})
        feed.remove_item(child)
        del wordlists[gid]
    elif settings.appendlvl:
        appendstr = "<br><small><small>lvl: %.2g &nbsp;" % lvl + \
                    "maxcmplvl: %.2f</small></small>" % maxcmplvl
        feed.append_description(child, appendstr)
        if content != "":
            feed.append_content(child, appendstr)
    logging.info("%.2g %.2f " % (lvl, maxcmplvl) + title)

if settings.outputfile is None:
    # Write output to console
    feed.print()
else:
    # Write output to file
    feed.write(settings.outputfile)
