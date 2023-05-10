#!/bin/python3.6
import os
import time
import re

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-t", "--interval", type="int", default=1, dest="interval",
                  help="--interval interval print")
parser.add_option("-m", "--mode", type="string", default="all", dest="mode",
                  help="--mode  all/total")
parser.add_option("-b", "--block", type="string", default="", dest="block",
                  help="--block  specify device")
parser.add_option("-l", "--total", action="store_true", dest="total",
                  help="--total caulase all iops")
(options, args) = parser.parse_args()

lines=open("/proc/diskstats", 'r').readlines()
olddata=[]
new_totaldata=[0, 0 ,0 ,0]
old_totaldata=[0, 0 ,0 ,0]
for i in range(len(lines)):
  line = re.sub(" +"," ",lines[i])
  items=line.strip().split(" ")[2:]
  olddata.append(items)


while 1:
  lines=open("/proc/diskstats", 'r').readlines()
  print("%6s %10s %10s %10s %10s %10s %10s %10s %10s %10s %10s"%("block","rd","wr","rKb","wKb", "r_merge","r_t","w_merge","w_t", "rq_num","in_que"))
  for i in range(len(lines)):
    line = re.sub(" +"," ",lines[i])
    items=line.strip().split(" ")[2:]
    olditems=olddata[i]
    if options.block:
        if options.block == items[0]:
            print("%6s %10d %10d %10d %10d"%(items[0],
                   int(items[1]) - int(olditems[1]), int(items[5]) - int(olditems[5]),
                   int(items[3]) - int(olditems[3]), int(items[7]) - int(olditems[7])))
        continue
    if options.total:
        new_totaldata[0] += int(items[1]) - int(olditems[1])
        new_totaldata[1] += int(items[5]) - int(olditems[5])
        new_totaldata[2] += int(items[3]) - int(olditems[3])
        new_totaldata[3] += int(items[7]) - int(olditems[7])
        new_totaldata[4] += int(items[2]) - int(olditems[2])

    print("%6s %10d %10d %10d %10d %10d %10d %10d %10d %10d %10d"%(items[0],
           int(items[1]) - int(olditems[1]), int(items[5]) - int(olditems[5]),
           int(items[3]) - int(olditems[3]), int(items[7]) - int(olditems[7]),
           int(items[2]) - int(olditems[2]), int(items[4]) - int(olditems[4]),
           int(items[6]) - int(olditems[6]), int(items[8]) - int(olditems[8]),
           int(items[9]), int(items[10]) - int(olditems[10])))
           #int(items[9]) - int(olditems[9]), int(items[10]) - int(olditems[10])))
    olddata[i]=items
  print("%6s %10d %10d %10d %10d"%("all",
         int(new_totaldata[0]) - int(old_totaldata[0]), int(new_totaldata[1]) - int(old_totaldata[1]),
         int(new_totaldata[2]) - int(old_totaldata[2]), int(new_totaldata[3]) - int(old_totaldata[3])))
  old_totaldata[0] = new_totaldata[0]
  old_totaldata[1] = new_totaldata[1]
  old_totaldata[2] = new_totaldata[2]
  old_totaldata[3] = new_totaldata[3]
  print("")
  time.sleep(options.interval)


