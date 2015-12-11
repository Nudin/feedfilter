#!/usr/bin/env python3
import comparetext as comp
import sys

txt_1=open(sys.argv[1], 'rU').read()
txt_2=open(sys.argv[2], 'rU').read()
print(comp.comp_txt(txt_1, txt_2))
