import os
import re
import json
import subprocess
import random

if not os.path.exists("/root/test.data"):
    os.system("dd if=/dev/zero of=~/test.data oflag=direct bs=1M count=128")
os.system("echo 1 > /sys/kernel/mm/kidled/use_hierarchy")
os.system("echo 15 > /sys/kernel/mm/kidled/scan_period_in_seconds")
os.system("mkdir -p /cgroup/memory")
os.system("mount -tcgroup -o memory /cgroup/memory")
os.system("echo 1 > /cgroup/memory/memory.use_hierarchy")
os.system("mkdir -p /cgroup/memory/test")
os.system("echo 1 > /cgroup/memory/test/memory.use_hierarchy")
os.system("echo $$ > /cgroup/memory/test/cgroup.procs")
os.system("dd if=~/test.data of=/dev/null bs=1M count=128")
print("wait a few mintunes and cat /cgroup/memory/test/memory.idle_page_stats | grep cfei")


