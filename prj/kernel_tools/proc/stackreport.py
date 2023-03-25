#!/bin/python3
import os
import re

listdir=os.listdir("/proc/")
diskkey={}
for item in listdir:
    ptask_dir="/proc/"+item+"/task"
    if os.path.exists(ptask_dir):
        listthread=os.listdir(ptask_dir)
        for thread in listthread:
            thread_stack_path =ptask_dir+"/"+thread+"/stack"
            thread_stat_path =ptask_dir+"/"+thread+"/stat"
            statres = open(thread_stat_path,'r').read()

            #get D process
            taskstat=re.sub(' +', ' ', statres[:-1]).split(" ")
            #print(taskstat)
            #print(taskstat[2])
            if taskstat[2][0] != "D":
                continue

            #print(thread_stat_path, taskstat[2])
            #continue;
            stackres = open(thread_stack_path,'r').read()
            if stackres in diskkey.keys():
                 dumpinfo=diskkey[stackres]
                 dumpinfo["cnt"] += 1
                 tasklist = dumpinfo["task"]
                 tasklist.append(thread)
            else:
                dumpinfo={}
                tasklist=[]
                tasklist.append(thread)
                dumpinfo["cnt"]=1
                dumpinfo["task"] = tasklist
                diskkey[stackres]=dumpinfo;

for key in diskkey.keys():
    #print(key, diskkey[key])
    print("task D list:",diskkey[key])
    print("task number:", diskkey[key]["cnt"])
    print(key)
