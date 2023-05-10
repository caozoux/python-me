#!/bin/python3

import sys
import os
import re

def dump_irq(cpunum):
    res=open("/proc/interrupts", 'r').readlines()
    array=[]
    for i in range(1, len(res)):
        irqnums=0
        line =re.sub(" +", " ", res[i][:-1].strip())
        item = line.split(" ")[1:]
        for i in range(cpunum):
        print(item)
        print(line)


res=os.popen("lscpu  | grep \"CPU:\" | awk '{print $2}'", 'r').read()[:-1]
CPU_NUM = int(res)

dump_irq(CPU_NUM)
