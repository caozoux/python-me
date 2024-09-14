#!/bin/python3

import sys
import os
from collections import defaultdict

report_key = defaultdict(int)
lines=open(sys.argv[1],'r').readlines()
for line in lines:
  items=line.split(" ")
  try:
    key= ";".join(items[0].split(";")[1:])
    report_key[key] += int(items[1][:-1])
  except ValueError:
    continue
  
#for key in report_key.keys():
#  print(key, report_key[key])
sorted_dict2 = dict(sorted(report_key.items(), key=lambda item: item[1]))
for item in sorted_dict2:
  print(item, report_key[item])
