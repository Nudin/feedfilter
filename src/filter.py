import os
import re
from utils import *

class Filter():
    
    def __init__(self, filterdir):
        self.blackwords = {}
        self.exactblackwords = {}
        self.filterdir=filterdir


    def read_filterlist(self, filename):
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

    def check(self, text, multiplier):  
        ltext=text.lower()
        lvl = 0
        for word in self.blackwords:
            if ltext.find(word) != -1:
                lvl += multiplier*self.blackwords[word]
        for word in self.exactblackwords:
            if text.find(word) != -1:
                lvl += multiplier*self.exactblackwords[word]
        return lvl

