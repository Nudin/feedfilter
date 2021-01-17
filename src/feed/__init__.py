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
import xml.etree.ElementTree as etree

from .atom import ATOM_URL, AtomFeed
from .rss import RssFeed


def get_feed(feed_file):
    """
    Determine the format of the feed and parse it
    """
    tree = etree.parse(feed_file)
    root = tree.getroot()
    if root.tag == "{%s}feed" % ATOM_URL:
        return AtomFeed(tree)
    if root.tag == "rss":
        return RssFeed(tree)
    raise NotImplementedError("Unknown feedformat!")
