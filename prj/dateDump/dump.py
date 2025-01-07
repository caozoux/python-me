#!/bin/python3

import os
import sys
import re

if not os.path.exists(sys.argv[1]):
  print("file not exits");
  exit(0)

avg_array=[]
lines=open(sys.argv[1], 'r').readlines()
line=lines[0][:-1]
res=re.sub(' +', ' ', line).strip()
item_size=len(res.split(" "))
avg_len=len(lines)

for i in range(item_size):
  avg_array.append(0)

for line in lines:
   res=re.sub(' +', ' ', line).strip()
   items = res.split(" ")
   lat ,nor_lat ,be_lat ,lc_lat ,idle_lat  ,hirq ,sirq ,lc_sys ,lc_usage ,sleep_usage ,D_usage ,io_usage = map(float, items[1:])
   for i in range(1, item_size):
     avg_array[i] += float(items[i])
   
   #if io_usage != 0:
   # print(res)
for i in range(item_size):
  avg_array[i] = round(avg_array[i]/avg_len,2)

print(avg_array)

for line in lines:
   res=re.sub(' +', ' ', line).strip()
   items = res.split(" ")
   lat ,nor_lat ,be_lat ,lc_lat ,idle_lat  ,hirq ,sirq ,lc_sys ,lc_usage ,sleep_usage ,D_usage ,io_usage = map(float, items[1:])
   for i in range(1, item_size):
     if float(items[i]) > (avg_array[i]*3):
      print(res)

