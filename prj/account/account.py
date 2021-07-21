import os
import sys


prev_total=0
buflist=open("./test", 'r').readlines()

#print('测试0\033[1;31;43m 测试1')
for line in buflist:
    item=line[:-1].split(" ")
    cursize = int(item[9],16)
    realtotal =  int(item[12],16)

    print(line[:-1])
    #print(item[10], item[9], item[12])
    if 'memblock_insert_region' in line:
        curtotal = prev_total + cursize
    elif 'memblock_add_range' in line:
        curtotal = prev_total + cursize
    elif 'memblock_remove_region' in line:
        curtotal = prev_total - cursize
    elif 'memblock_isolate_range' in line:
        curtotal = prev_total - cursize
    else:
        print("error", line)
        exit(1)
    #print("prev: %x  cursize:%x = %x %x"%(prev_total, cursize, curtotal, realtotal))

    if curtotal != realtotal:
        #print('\033[1;31;43m', end='')
        print('\033[46merror  %x -ne %x \033[0m'%(curtotal, realtotal))
        exit(1)
        #print(end=nd)

    prev_total = realtotal
