#!/bin/python3

import os
import sys
import re

filename=sys.argv[1]

if not os.path.exists(filename):
  exit(1)

res=open(filename, 'r').readlines()
iodict={}
cnt=0

for line in res:
  cnt += 1;
  if line[:3] == "253":
    linelist= re.sub(" +"," ",line).split(" ")
    status = linelist[5]
    offset = linelist[7]
    blksize = linelist[9]
    #print(linelist)
    #print(linelist, status ,offset, blksize)
    if status == 'Q':
      #print("find")
      #key=offset+"+"+blksize
      key=offset
      iodict[key] = linelist
    if status == 'C' or status == 'M' :
      #key=offset+"+"+blksize
      key=offset
      if key in iodict.keys():
        #print("del")
        del iodict[key]

for key in iodict.keys():
  print(iodict[key])
#print(iodict)
