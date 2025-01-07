#!/bin/python3

import sys
import os


memcg_dict={}
slab_info_dict={}

lines=open("/proc/slabinfo", 'r').readlines()
for line in lines[2:]:
  items =line.split();
  name, active_objs, num_objs, obj_size = items[0:4]
  slab_info_dict[name] = int(obj_size)


lines=open("/sys/kernel/debug/memcg_slabinfo", 'r').readlines()

for line in lines[1:]:
  items =line.split();
  name, css_id, active_objs, num_objs, active_slabs, num_slabs = items
  if css_id in memcg_dict.keys():
    dict_l1 = memcg_dict[css_id]
  else:
    dict_l1 = {}
    memcg_dict[css_id] = dict_l1;
  
  if name in dict_l1.keys(): 
    array_list = dict_l1[name]
    array_list[0] += int(active_slabs)
    array_list[1] += int(num_objs)
    array_list[2] += int(active_slabs)
    array_list[3] += int(num_slabs)
  else:
    dict_l1[name] = [int(active_slabs), int(num_objs), int(active_slabs), int(num_slabs)]


memcg_slab_total_dict={}
memcg_slab_total = 0

for key in memcg_dict.keys():
  dict_l1 = memcg_dict[key]
  total_size = 0
  for key_l1 in dict_l1.keys():
    total_size += dict_l1[key_l1][1] * slab_info_dict[key_l1]
  memcg_slab_total_dict[key] = total_size
  memcg_slab_total += total_size

sorted_dict_by_value = dict(sorted(memcg_slab_total_dict.items(), key=lambda item: item[1]))
for item in sorted_dict_by_value:
  print("cproup id:%-10s kmem(Mb):%-8d"%(item, int(memcg_slab_total_dict[item]/1024/1024)))
res=os.popen("cat /proc/meminfo  | grep Slab").read()
meminfo_slab=int(res.split(":")[1].strip().split(" ")[0])
print("cgroup total kmem:", memcg_slab_total/1024/1024)
print("meminfo slab:", meminfo_slab/1024)
