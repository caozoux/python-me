#!/bin/python3
import os
from collections import defaultdict

topcnt=10

context=open("log", 'r').readlines()
#print(res[2:-2])
for res in context:
  res1=res[2:-3].replace("), (","\n").replace(", ", " ")
  total_cnt=0
  last_cnt=0
  top5_cnt=0
  pr_list = res1.split("\n")
  report= defaultdict(int)
  inode_report= defaultdict(lambda: defaultdict(int))

  for line in pr_list:
    array=line.split(" ")
    num=int(array[-1][:-1])
    total_cnt += num

  for line in pr_list:
    array=line.split(" ")
    num=int(array[-1][:-1])
    #print(line.replace("u'","").replace("' ","_"))
    l1_array=line.replace("u'","").replace("' ","+").split("+")
    if len(l1_array) < 2:
      continue
    l2_list = l1_array[0].split("-",2)
    l2_comm = l2_list[2]
    l2_data = int(l1_array[1][:-1])
    l2_inode = l2_list[1]
    #print(l2_comm, l2_data)
    report[l2_comm] += l2_data
    inode = inode_report[l2_comm]
    inode[l2_inode] += l2_data
    
    last_cnt += num
    

  report_list = sorted(report.items(), key=lambda x: x[1])
  for item in report_list[-topcnt:]:
    print(item)
    inode= inode_report[item[0]]
    inode_list = sorted(inode.items(), key=lambda x: x[1])
    #for inode_item in inode_list:
    #  print(inode_item)
    top5_cnt += item[1]
  print("total:%-10d top5:%-10d"%(total_cnt, top5_cnt))
  exit(0)
