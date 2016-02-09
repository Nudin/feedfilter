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
import math
import os
from collections import Counter
import re
import logging
from gettext import gettext as _

filedir = os.path.join(os.path.dirname(__file__), os.path.pardir,
                       "include", "commonwords")

common_words = {}
for lang in os.listdir(filedir):
    try:
        filename = os.path.join(filedir, lang)
        common_words[lang] = open(filename, 'rU').read().split()
    except Exception:
        logging.warn(_("Can't load file %s") % common_words[lang])
        pass

# we remove all special characters from the text before splitting it into words
specialchar_filter = re.compile('[^\w\s]+', re.UNICODE)

# For the comparison we ignore all "words"
# only consisting of digits,
# of length one and
# of length two or three witch are not written in UPPER case
re_filters = ['\d+$', '\w$', '[A-Z][a-z]{1,2}$']
compiled_re_filters = (re.compile(i) for i in re_filters)


def analyse(lang, txt):
    txt = specialchar_filter.sub('', txt)

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
        return wordlist
    else:
        logging.warn(_("No commonwords-list available for language %s") % lang)
        return wordlist


def comp(dict_1, dict_2):
    norm_1 = math.sqrt(sum(dict_1[key]*dict_1[key]*len(key) for key in dict_1))
    norm_2 = math.sqrt(sum(dict_2[key]*dict_2[key]*len(key) for key in dict_2))

    sp = sum(dict_1[key]*dict_2.get(key, 0)*len(key) for key in dict_1)
    n = norm_1*norm_2
    if n == 0:
        return 0
    else:
        return sp/n


def comp_txt(txt_1, txt_2):
    dict_1 = analyse(txt_1)
    dict_2 = analyse(txt_2)
    return comp(dict_1, dict_2)
