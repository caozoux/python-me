import os
import time

lines=open("/proc/diskstats", 'r').readlines()
olddata=[0,0,0,0,0,0,0]
for i in range(len(lines)):
  line = lines[i]
  items=line.strip()[10:].split(" ")
  olddata[i]=items


while 1:
  
  lines=open("/proc/diskstats", 'r').readlines()
  print("%6s %15s %15s %15s %15s"%("block","rd","wr","rKb","wKb"))
  for i in range(len(lines)):
    line = lines[i]
    items=line.strip()[10:].split(" ")
    olditems=olddata[i]
    if items[0] == "sda2":
      print("%6s %15d %15d %15d %15d"%(items[0],
           int(items[1]) - int(olditems[1]), int(items[5]) - int(olditems[5]),
           int(items[3]) - int(olditems[3]), int(items[7]) - int(olditems[7])))
    olddata[i]=items
  print("")
  time.sleep(1)
