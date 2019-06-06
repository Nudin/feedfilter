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
import logging
import math
import os
import re
from collections import Counter
from gettext import gettext as _
from typing import Tuple

filedir = os.path.join(
    os.path.dirname(__file__), os.path.pardir, "include", "commonwords"
)

common_words = {}
for lang in os.listdir(filedir):
    try:
        filename = os.path.join(filedir, lang)
        common_words[lang] = open(filename, "rU").read().split()
    except Exception:
        logging.warning(_("Can't load file %s") % common_words[lang])
        pass

# we remove all special characters from the text before splitting it into words
specialchar_filter = re.compile("[^\w\s]+", re.UNICODE)

# For the comparison we ignore all "words"
# only consisting of digits,
# of length one and
# of length two or three witch are not written in UPPER case
re_filters = ["\d+$", "\w$", "[A-Z][a-z]{1,2}$"]
compiled_re_filters = (re.compile(i) for i in re_filters)


def analyse(lang, *txt) -> Tuple[Counter, float]:
    txt = " ".join(txt)
    txt = specialchar_filter.sub("", txt)

    wordlist = Counter(txt.split())

    for word in list(wordlist):
        for re_filter in compiled_re_filters:
            if re_filter.match(word):
                del wordlist[word]

    wordlist = dict((k.lower(), v) for k, v in wordlist.items())

    if lang in common_words:
        for word in common_words[lang]:
            try:
                del wordlist[word]
            except KeyError:
                continue
    else:
        logging.warning(_("No commonwords-list available for language %s") % lang)

    norm = math.sqrt(sum(value * value * len(key) for key, value in wordlist.items()))

    return (wordlist, norm)


def comp(wordlist_1, wordlist_2):
    dict_1, norm_1 = wordlist_1
    dict_2, norm_2 = wordlist_2

    # For performance: make sure dict_2 is shorter
    if len(dict_1) < len(dict_2):
        dict_1, dict_2 = dict_2, dict_1

    sp = sum(value * dict_1.get(key, 0) * len(key) for key, value in dict_2.items())
    n = norm_1 * norm_2
    if n == 0:
        return 0
    else:
        return sp / n


def comp_txt(txt_1, txt_2):
    dict_1 = analyse(txt_1)
    dict_2 = analyse(txt_2)
    return comp(dict_1, dict_2)
