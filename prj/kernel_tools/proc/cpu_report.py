#!/bin/python3

import time
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interval", type="int", dest="interval", default="1",
                  help="--interval interval ")
(options, args) = parser.parse_args()

def get_cpu_load():
    with open('/proc/stat', 'r') as file:
        lines = file.readlines()

    cpu_load = []
    for line in lines:
        if line.startswith('cpu'):
            cpu_stats = line.split()
            cpu_load.append(cpu_stats)

    return cpu_load

def cpu_load_report():
    cpu_load_old = get_cpu_load()
    time.sleep(options.interval)
    cpu_load_new = get_cpu_load()
    for i in range(len(cpu_load_old)):
        cpu_stats = cpu_load_old[i]
        cpu_name = cpu_stats[0]
        user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice = map(int, cpu_stats[1:])
        total = user + nice + system + idle + iowait + irq + softirq + steal + guest + guest_nice
        cpu_stats = cpu_load_new[i]
        new_user, new_nice, new_system, new_idle, new_iowait, new_irq, new_softirq, new_steal, new_guest, new_guest_nice = map(int, cpu_stats[1:])
        new_total = new_user + new_nice + new_system + new_idle + new_iowait + new_irq + new_softirq + new_steal + new_guest + new_guest_nice
        usage = 100*(new_system - system)/(new_total - total)
        user_usage = 100*(new_user - user)/(new_total - total)
        system_usage = 100*(new_system - system)/(new_total - total)
        softirq_usage = 100*(new_softirq - softirq)/(new_total - total)
        irq_usage = 100*(new_irq - irq)/(new_total - total)
        print("%-8s %-8.2f %-8.2f %-8.2f %-8.2f"%(cpu_name, user_usage, system_usage, softirq_usage, irq_usage))

print("%-8s %-8s %-8s %-8s %-8s"%("cpu", "user", "system", "softirq", "hwirq"))
while True:
    cpu_load_report()

