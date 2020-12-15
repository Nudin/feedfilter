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
import logging
from collections import Counter
from typing import Tuple

import comparetext
import logger
from feed import get_feed
from filter import Filter
from settings import Settings

# setup gettext
gettext.textdomain("feedfilter")

# parse commandline arguments and settingsfile
settings = Settings()
settings.read_argv()
settings.read_settings()

# Start Logger
logger.setupLogger(settings)

# read and parse filterfiles
wordfilter = Filter(settings)
wordfilter.read_filterlist("./blackwordlist.txt")
wordfilter.read_filterlist(settings.sitename)

# Parse feed
feed = get_feed(settings.feedfile)
# For now we use the language without any regional variants
lang = feed.lang.split("-")[0]

for child in feed:
    # Check for duplicates
    max_similarity = 0
    child.wordlist: Tuple[Counter, float] = comparetext.analyse(
        lang, child.title, child.description, child.content
    )
    for child2 in feed:
        if child.id == child2.id or not hasattr(child2, "wordlist"):
            break
        similarity = comparetext.comp(child.wordlist, child2.wordlist)
        max_similarity = max(max_similarity, similarity)
        if similarity > settings.cmp_threshold:
            child2.add_crosslink(child.link, child.title)
            logging.warning(
                "removing news entry: %s as duplicate of: %s",
                child.title,
                child2.title,
            )
    if max_similarity > settings.cmp_threshold:
        feed.remove_item(child)
        continue

    # Check against blackwords
    lvl = wordfilter.check(child.title, settings.title_scale)
    if child.content:
        lvl += wordfilter.check(child.content, 1)
    elif child.description:
        lvl += wordfilter.check(child.description, 1)
    if lvl > settings.threshold:
        logging.warning("removing item %s with score %i", child.title, lvl)
        feed.remove_item(child)
    elif settings.appendlvl:
        appendstr = (
            "<br><small><small>lvl: %.2g/%g &nbsp;" % (lvl, settings.threshold)
            + "maxcmplvl: %.2f</small></small>" % max_similarity
        )
        child.append_description(appendstr)
        if child.content != "":
            child.append_content(appendstr)
    logging.info("%.2g %.2f " % (lvl, max_similarity) + child.title)

if settings.outputfile is None:
    # Write output to console
    feed.print()
else:
    # Write output to file
    feed.write(settings.outputfile)
