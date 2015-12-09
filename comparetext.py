#!/usr/bin/env python3
import math
from collections import Counter
import re
import sys

def comp():
    common_words = open('de-commonwordlist.txt', 'rU').read().split()
    re_filters = ['\W+\d+\W+', '\W+\w\W+', '(\W+[A-Z][a-z]{1,2})+\W+' ]
    
    specialchar_filter = re.compile('[^\w\s]+', re.UNICODE)
    compiled_re_filters = (re.compile(i) for i in re_filters)
    
    txt_1=open(sys.argv[1], 'rU').read()
    txt_2=open(sys.argv[2], 'rU').read()
    
    txt_1=specialchar_filter.sub('', txt_1)
    txt_2=specialchar_filter.sub('', txt_2)
    for re_filter in compiled_re_filters:
        txt_1=re_filter.sub(' ', txt_1)
        txt_2=re_filter.sub(' ', txt_2)
    
    dict_1=Counter(txt_1.lower().split())
    dict_2=Counter(txt_2.lower().split())
    
    for word in common_words:
        del dict_1[word]
        del dict_2[word]
    
    for key in dict_1:
        if dict_1[key] !=0 and dict_2.get(key, 0) != 0:
            1+1
            #print(key,dict_1[key],dict_2.get(key, 0)) 
    
    norm_1=math.sqrt(sum(dict_1[key]*dict_1[key]*len(key) for key in dict_1))
    norm_2=math.sqrt(sum(dict_2[key]*dict_2[key]*len(key) for key in dict_2))
    
    sp=sum(dict_1[key]*dict_2.get(key, 0)*len(key) for key in dict_1)
    print(sp, norm_1, norm_2)
    print(sp/(norm_1*norm_2))

comp()

# Note:
# Div through zero if one txt is empty
