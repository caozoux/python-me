#!/bin/python3

import os
import sys
import re
import time

record_list=[]
cnt=20;
while cnt > 0:
    item=[]
    lines=os.popen("cat /sys/kernel/debug/sched/debug | grep  --no-group-separator -A 1 \"cpu#\"").readlines()
    size=int(len(lines)/2)
    for i in range(size):
        cpu=lines[i*2][:-1].split(",")[0][4:]
        nr_running=lines[i*2+1][:-1].split(":")[1].strip()
        item.append([int(cpu), int(nr_running)])
    record_list.append(item)
    time.sleep(0.1)
    cnt -= 1;
for item in record_list:
    print(item)
