#!/bin/python3
import os
import time

meminfo_dict={}
old_meminfo_dict={}
default_sleep=1

memtypelist=[
"MemTotal",
"MemFree",
"MemAvailable",
"Buffers",
"Cached",
"SwapCached",
"Active",
"Inactive",
"Active(anon)",
"Inactive(anon)",
"Active(file)",
"Inactive(file)",
"Unevictable",
"Mlocked",
"SwapTotal",
"SwapFree",
"Dirty",
"Writeback",
"AnonPages",
"Mapped",
"Shmem",
"KReclaimable",
"Slab",
"SReclaimable",
"SUnreclaim",
"KernelStack",
"PageTables",
"NFS_Unstable",
"Bounce",
"WritebackTmp",
"CommitLimit",
"Committed_AS",
"VmallocTotal",
"VmallocUsed",
"VmallocChunk",
"HardwareCorrupted",
"AnonHugePages",
"ShmemHugePages",
"ShmemPmdMapped",
"InCgroup(File)",
"InCgroup(Dirty)",
"HugePages_Total",
"HugePages_Free",
"HugePages_Rsvd",
"HugePages_Surp",
"Hugepagesize",
"Hugetlb",
"DirectMap4k",
"DirectMap2M",
]

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()

if options.list:
    for item in memtypelist:
        print(item)

if options.interval:
    default_sleep=options.interval

lines=open("/proc/meminfo", 'r').readlines()

for line in lines:
    array = line.split(":")
    name=array[0]
    val=int(array[1].strip().replace(" kB", ""))
    old_meminfo_dict[name]=val

for line in lines:
    array = line.split(":")
    name=array[0]
    val=int(array[1].strip().replace(" kB", ""))
    meminfo_dict[name]=val

print(meminfo_dict)
#time.sleep(1)
