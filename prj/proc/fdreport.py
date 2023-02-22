#!/bin/python3
import os


listdir=os.listdir("/proc/")
for item in listdir:
    ptask_dir="/proc/"+item+"/task"
    if os.path.exists(ptask_dir):
        listthread=os.listdir(ptask_dir)
        for thread in listthread:
            thread_openfd_dir=ptask_dir+"/"+thread+"/fd"
            fdlist=os.listdir(thread_openfd_dir)
            for fd in fdlist:
                fdpath=os.path.join(thread_openfd_dir, fd)
                try:
                    #print(fdpath, os.stat(fdpath));
                    print(fdpath, os.readlink(fdpath));
                except Exception as e:
                    continue

