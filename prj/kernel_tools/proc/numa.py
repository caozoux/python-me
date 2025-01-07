#!/bin/python3

import time
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interval", type="int", dest="interval", default="1",
                  help="--interval interval ")
(options, args) = parser.parse_args()

def get_numa_stat():
    with open('/proc/vmstat', 'r') as file:
        lines = file.readlines()

    numa_stat = []
    for line in lines:
        if line.startswith('numa'):
            item = line.split()[1]
            numa_stat.append(item)

    return numa_stat

def numa_stat_report():
    numa_stat_old = get_numa_stat()
    time.sleep(options.interval)
    numa_stat_new = get_numa_stat()
    numa_hit_old, numa_miss_old, numa_foreign_old, numa_interleave_old, numa_local_old, numa_other_old, numa_pte_update_old, numa_huge_pte_updates_old, numa_hint_faults_old, numa_hint_faults_local_old, numa_pages_migrated_old = map(int, numa_stat_old)
    numa_hit_new, numa_miss_new, numa_foreign_new, numa_interleave_new, numa_local_new, numa_other_new, numa_pte_update_new, numa_huge_pte_updates_new, numa_hint_faults_new, numa_hint_faults_local_new, numa_pages_migrated_new = map(int, numa_stat_new)
    #user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice = map(int, cpu_stats[1:])
    #print("%-8s %-8.2f %-8.2f %-8.2f %-8.2f"%(cpu_name, user_usage, system_usage, softirq_usage, irq_usage))
    print("%-20d %-20d %-20d %-20d %-20d %-20d %-20d %-20d %-20d %-20d %-20d"%(numa_hit_new - numa_hit_old, numa_miss_new - numa_miss_old, numa_foreign_new - numa_foreign_old, numa_interleave_new - numa_interleave_old, numa_local_new - numa_local_old, numa_other_new - numa_other_old, numa_pte_update_new - numa_pte_update_old, numa_huge_pte_updates_new - numa_huge_pte_updates_old, numa_hint_faults_new - numa_hint_faults_old, numa_hint_faults_local_new - numa_hint_faults_local_old, numa_pages_migrated_new - numa_pages_migrated_old))

print("%-20s %-20s %-20s %-20s %-20s %-20s %-20s %-20s %-20s %-20s %-20s"%("numa_hit", "numa_miss", "numa_foreign", "numa_interleave", "numa_local", "numa_other", "numa_pte_update", "numa_huge_pte_updates", "numa_hint_faults", "numa_hint_faults_local", "numa_pages_migrated"))
while True:
    numa_stat_report()

