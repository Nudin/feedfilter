import os
import re
from utils import *

class Filter():
    """
    Match a set of blacklisted words against a text
    """
    
    def __init__(self, filterdir):
        """
        Initialise the filter

        filterdir: the directory in witch the filterlists are located
        """
        self.blackwords = {}
        self.exactblackwords = {}
        self.filterdir=filterdir


    def read_filterlist(self, filename):
        """
        Read a set of wordfilters from a file

        filename: the filename, relative to filterdir

        The format of the entries in the filterfile is:
        [#][^\t]*(\t|  +)[-0-9]*

        Lines starting with the character '#' are ignored.
        All other lines should contain a filterstring and an filtervalue
        seperated by a single tab (\t) or two or more spaces.

        The strings are handled case intensive, except if the are less or equal
        four digits long or written completely in UPPER CASE.
        """
        c = re.compile('  +')
        try:
            with open(os.path.join(self.filterdir, filename), 'rU') as infile:
                for line in infile:
                    if line[0] == "#":
                        continue
                    if len(line) <= 1:
                        continue
                    tmp=c.sub('\t', line.strip()).split('\t')
                    try:
                        if len(tmp[0]) <= 3 or tmp[0].isupper():
                            self.exactblackwords[tmp[0]]=float(tmp[1])
                        else:
                            self.blackwords[tmp[0].lower()]=float(tmp[1])
                    except:
                        warn("Cannot parse line in", filename, ":")
                        warn(line)
                        continue
        except IOError:
            warn('error opening file:', filename)

    def check(self, text, multiplier=1):
        """
        Check a text against the filter

        text: the string the filter should be matched against
        multiplier: multiply the weight of all matching filters with this constant
        """
        ltext=text.lower()
        lvl = 0
        for word in self.blackwords:
            if ltext.find(word) != -1:
                lvl += multiplier*self.blackwords[word]
        for word in self.exactblackwords:
            if text.find(word) != -1:
                lvl += multiplier*self.exactblackwords[word]
        return lvl

