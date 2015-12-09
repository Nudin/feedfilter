#!/usr/bin/env python3
import math
from collections import Counter
import re
import sys

#@profile
def comp():
    common_words = open('de-commonwordlist.txt', 'rU').read().split()
    re_filters = ['\d+$', '\w$', '[A-Z][a-z]{1,2}$' ]
    
    specialchar_filter = re.compile('[^\w\s]+', re.UNICODE)
    compiled_re_filters = (re.compile(i) for i in re_filters)
    
    txt_1=open(sys.argv[1], 'rU').read()
    txt_2=open(sys.argv[2], 'rU').read()
    
    txt_1=specialchar_filter.sub('', txt_1)
    txt_2=specialchar_filter.sub('', txt_2)
    
    dict_1=Counter(txt_1.split())
    dict_2=Counter(txt_2.split())

    for word in list(dict_1):
        for re_filter in compiled_re_filters:
            if re_filter.match(word):
                del dict_1[word]
    for word in list(dict_2):
        for re_filter in compiled_re_filters:
            if re_filter.match(word):
                del dict_2[word]

    dict_1=dict((k.lower(), v) for k,v in dict_1.items())
    dict_2=dict((k.lower(), v) for k,v in dict_2.items())

    for word in common_words:
        try:
           del dict_1[word]
           del dict_2[word]
        except KeyError:
            continue
    
    norm_1=math.sqrt(sum(dict_1[key]*dict_1[key]*len(key) for key in dict_1))
    norm_2=math.sqrt(sum(dict_2[key]*dict_2[key]*len(key) for key in dict_2))
    
    sp=sum(dict_1[key]*dict_2.get(key, 0)*len(key) for key in dict_1)
    print(sp, norm_1, norm_2)
    print(sp/(norm_1*norm_2))

for i in range(100):
    comp()

# Note:
# Div through zero if one txt is empty
