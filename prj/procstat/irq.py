#!/usr/bin/env python3
import os
import re
import sys

def dump_irq(cpus):
    """
    """
    irqdic={}
    res=open("/proc/interrupts",'r').readlines()
    array=[]

    for i in range(1,len(res)):
        irqnums=0
        irqname=""
        line= re.sub(" +", " ",res[i][:-1].strip())
        item = line.split(" ")[1:]
        if len(item) <= 2:
            continue
        for i in range(cpus):
            irqnums += int(item[i])
        irqname=' '.join(item[cpus:])
        irqdic[irqname] = irqnums
        #print(irqnums, item, irqname);
    return irqdic
CPU_NUM=0

res=os.popen("lscpu | grep \"^CPU(s):\" | awk '{print $2}'", 'r').read()[:-1]
CPU_NUM=int(res)
irqdict = dump_irq(CPU_NUM)
print(irqdict, );

