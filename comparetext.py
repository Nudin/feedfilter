#!/usr/bin/env python3
import math
import os
from collections import Counter
import re

dir = os.path.dirname(__file__)
common_words = open(os.path.join(dir,'de-commonwordlist.txt'), 'rU').read().split()
re_filters = ['\d+$', '\w$', '[A-Z][a-z]{1,2}$' ]
    
specialchar_filter = re.compile('[^\w\s]+', re.UNICODE)
compiled_re_filters = (re.compile(i) for i in re_filters)

#@profile
def analyse(txt):
    txt=specialchar_filter.sub('', txt)
    
    wordlist=Counter(txt.split())

    for word in list(wordlist):
        for re_filter in compiled_re_filters:
            if re_filter.match(word):
                del wordlist[word]

    wordlist=dict((k.lower(), v) for k,v in wordlist.items())

    for word in common_words:
        try:
           del wordlist[word]
        except KeyError:
            continue
    return wordlist

def comp(dict_1, dict_2):
    norm_1=math.sqrt(sum(dict_1[key]*dict_1[key]*len(key) for key in dict_1))
    norm_2=math.sqrt(sum(dict_2[key]*dict_2[key]*len(key) for key in dict_2))
    
    sp=sum(dict_1[key]*dict_2.get(key, 0)*len(key) for key in dict_1)
    #print(sp, norm_1, norm_2)
    return sp/(norm_1*norm_2)   # ToDo: avoid division by zero

def comp_txt(txt_1, txt_2):
    dict_1=analyse(txt_1)
    dict_2=analyse(txt_2)
    return comp(dict_1, dict_2)
