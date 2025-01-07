#!/bin/python3

import os
import sys
import time
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interval", type="int", dest="interval", default="1",
                  help="--interval interval ")
parser.add_option("-p", "--pid", type="int", dest="pid",
                  help="--pid specify pid monitor")

(options, args) = parser.parse_args()

def get_proc_list(path_name):
    print(path_name)
    with open(path_name, 'r') as file:
        lines = file.readlines()

    proc_list = []
    for line in lines:
        if line.startswith('  eth0'):
            proc_list.append(line.split())

    return proc_list

def pid_net_report(path_name):

    cpu_load_old = get_proc_list(path_name)
    time.sleep(options.interval)
    cpu_load_new = get_proc_list(path_name)

    face, bytes, packets, errs, drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice = map(int, cpu_stats[1:])
    print(cpu_load_new)

if not options.pid:
    print("please specify pid")
    exit(1)

pid_net_package="/proc/"+str(options.pid)+"/net/dev"
if not os.path.exists(pid_net_package):
    print(pid_net_package, "not find")
    exit(1)

while True:
    pid_net_report(pid_net_package)

