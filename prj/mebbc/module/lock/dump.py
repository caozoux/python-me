#!/bin/python3

import os
import sys
from collections import defaultdict

report_key=defaultdict(list)

if not os.path.exists(sys.argv[1]):
  print("Err: %s not find"%sys.avg[1])

lines=open(sys.argv[1],'r').readlines();
#2024-05-13 16:47:31 java,3375770,ffffffffa4e4f1c0,mutex_unlock,proc_cgroup_show,proc_single_show,seq_read_iter,seq_read,vfs_read,ksys_read,do_syscall_64,entry_SYSCALL_64_after_hwframe, wait_latency:6983880532 run_latency:46910 sched_latency:13670
for line in lines:
  item=line.strip().split(" ")
  if len(item) <= 3:
    continue
  info=" ".join(item[2:-3]).split(",")
  comm =info[0]
  pid = info[1]
  address = info[2]
  wait_latency = int(item[-3].split(":")[1])
  run_latency = int(item[-2].split(":")[1])
  sched_latency = int(item[-1].split(":")[1])
  #sched_latency = 0
  #key=address+","+",".join(info[4:])
  key=address
  report_key[key].append([wait_latency, run_latency, sched_latency, comm,pid, ",".join(info[4:])])
  #print(key)
  #print(comm,pid,address,",".join(info[4:]), wait_latency, run_latency, sched_latency)
  #print(report_key)

sorted_items = sorted(report_key.items(), key=lambda item: len(item[1]), reverse=True)
for item in sorted_items:
   
  print("lockaddr:",item[0])
  sub_key=defaultdict(list)
  avg_wait = [0, 0, 0]
  
  for item_l1 in item[1]:
    avg_wait[0] += item_l1[0]
    avg_wait[1] += item_l1[1]
    avg_wait[2] += item_l1[2]
    sub_key[item_l1[5]].append([item_l1[3],item_l1[4], item_l1[0], item_l1[1], item_l1[2]])
  print("  ","wait:",avg_wait[0]/len(item[1]), "run:", avg_wait[1]/len(item[1]), "sched:", avg_wait[2]/len(item[1]))

  for key in sub_key.keys():
    print("  ",key)
    for item_l2 in sub_key[key]:
      print("       %-16s %-8s %d %d %d"%(item_l2[0],item_l2[1], item_l2[2], item_l2[3], item_l2[4]))
  #for item_l1 in item[1]:
  #  print("   %-16s %-8s %d %d %d"%(item_l1[3],item_l1[4], item_l1[0], item_l1[1], item_l1[2]), item_l1[5])
exit(0)
for key in report_key.keys():
  print(key)
  for item in report_key[key]:
    print(item)

#  l_min_wait=0xfffffffffffff
#  l_max_wait=0
#  l_total_wait=0
#  for item in report_key[key]:


#    if l_min_wait > int(item[0]):
#      l_min_wait = int(item[0])
#    if l_max_wait < int(item[0]):
#      l_max_wait = int(item[0])
#  print(key, l_min_wait, l_total_wait/len(report_key[key]), l_max_wait)
