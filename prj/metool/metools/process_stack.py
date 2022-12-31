import os


listdir=os.listdir("/proc/15186/task/")
diskkey={}

for dir in listdir:
  newdir=os.path.join("/proc/15186/task/", dir)
  newstack=os.path.join(newdir, "stack")
  res = open(newstack,'r').read()
  if res in diskkey.keys():
    dumpinfo=diskkey[res]
    dumpinfo["cnt"] += 1
    tasklist = dumpinfo["task"]
    tasklist.append(dir)
  else:
    dumpinfo={}
    tasklist=[]
    tasklist.append(dir)
    dumpinfo["cnt"]=1
    dumpinfo["task"] = tasklist 
    diskkey[res]=dumpinfo;

for key in diskkey.keys():
  print(key, diskkey[key])

