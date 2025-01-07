#!/bin/bash

prev_node0=0
prev_node1=0
while true;
do
  now_node0=`cat /sys/fs/resctrl/mon_data/mon_L3_00/mbm_total_bytes`
  now_node1=`cat /sys/fs/resctrl/mon_data/mon_L3_01/mbm_total_bytes`
  mbm_node0=`echo $prev_node0 $now_node0 | awk '{printf("%.2f", ($2-$1)/1024/1024)}'`
  mbm_node1=`echo $prev_node1 $now_node1 | awk '{printf("%.2f", ($2-$1)/1024/1024)}'`
  printf "%-5s %-10s\n" Node MBM
  printf "%-5s %-10s\n" 0  $mbm_node0"M"
  printf "%-5s %-10s\n" 1  $mbm_node1"M"
  prev_node0=$now_node0
  prev_node1=$now_node1
  sleep 1
done
