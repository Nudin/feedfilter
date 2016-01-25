import os
import re
from utils import *

class Filter():
    
    def __init__(self, filterdir):
        self.blackwords = {}
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
                        self.blackwords[tmp[0]]=float(tmp[1])
                    except:
                        warn("Cannot parse line in", filename, ":")
                        warn(line)
                        continue
        except IOError:
            warn('error opening file:', filename)

    def check(self, text, multiplier):  
        lvl = 0
        for word in self.blackwords:
            if text.find(word) != -1:
                lvl += multiplier*self.blackwords[word]
        return lvl

