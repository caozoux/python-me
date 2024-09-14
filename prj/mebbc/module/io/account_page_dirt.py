#!/usr/libexec/platform-python

from __future__ import absolute_import
from __future__ import division
# Do not import unicode_literals until #623 is fixed
# from __future__ import unicode_literals
from __future__ import print_function

from bcc import BPF
from collections import defaultdict
from time import strftime

import argparse
import curses
import pwd
import re
import signal
from time import sleep

FIELDS = (
    "PID",
    "UID",
    "CMD",
    "HITS",
    "MISSES",
)
DEFAULT_FIELD = "HITS"
DEFAULT_SORT_FIELD = FIELDS.index(DEFAULT_FIELD)
# load BPF program
bpf_text = """

#include <uapi/linux/ptrace.h>
#include <linux/mm.h>
#include <linux/fs.h>
struct key_t {
    u64 ip;
    u32 pid;
    u32 uid;
    char block[8];
    char comm[32];
};

BPF_HASH(counts, struct key_t);

int do_count(struct pt_regs *ctx) {
    struct key_t key = {};
    struct address_space *mapping = (struct address_space *)ctx->si;
    u64 pid = bpf_get_current_pid_tgid();
    u32 uid = bpf_get_current_uid_gid();
    struct inode *inode = (struct inode *)mapping->host;

    key.ip = PT_REGS_IP(ctx);
    //key.pid = pid & 0xFFFFFFFF;
    key.pid = pid>>32;
    //key.uid = uid & 0xFFFFFFFF;
    bpf_get_current_comm(&(key.comm), 32);
    bpf_probe_read_kernel(&(key.block), 4, inode->i_sb->s_id);

    counts.increment(key);
    return 0;
}

"""
b = BPF(text=bpf_text)
b.attach_kprobe(event="account_page_dirtied", fn_name="do_count")
#b.attach_kprobe(event="__folio_mark_dirty", fn_name="do_count")
counts = b.get_table("counts")

exiting = 0
stats = defaultdict(lambda: defaultdict(int))
report= defaultdict(int)
stats_list = []
cnt=0
total_iops=0
topdickt={}
while 1:
    try:
        iotps = 0
        if exiting:
          exit(0)
        for k, v in counts.items():
            if not k.block == "sda2":
              continue;
        #    stats["%d-%d-%s" % (k.pid, k.uid, k.comm.decode('utf-8', 'replace'))][k.ip] = v.value
            #print(v.value)
            #report["%d-%d-%s" % (k.pid, k.uid, k.comm.decode('utf-8', 'replace'))] += v.value
            report["%s" % (k.comm.decode('utf-8', 'replace'))] += v.value
            iotps += v.value
            total_iops += int(iotps)
            pid = int(k.pid)
            #pid = str(k.comm)
            pid_iops= int(v.value)
            if pid in topdickt.keys():
              topdickt[pid] += pid_iops;
            else:
              topdickt[pid] = pid_iops;
            #report["%d" % (k.pid)] += 1
        #for pid, count in sorted(stats.items(), key=lambda stat: stat[0]):
        #  for k, v in count.items():
        #    _pid, uid, comm = pid.split('-', 2)
        #    stats_list.append(
        #        (int(_pid), uid, comm))
          #stats_list = sorted(
          #    stats_list, key=lambda stat: stat[DEFAULT_SORT_FIELD], reverse=True
          #)
        counts.clear()

        #print((stats))
        #print(len(stats))
        #print(len(report))
        #print((report))
        #report_list = sorted(report, key=lambda report: report[1], reverse=False)
        #if iotps > 3000:
        report_list = sorted(report.items(), key=lambda x: x[1])
        fd = open("log", 'a')
        fd.write("zz:" + str(report_list) + "\n")
        fd.flush()
        fd.close()
        print(report_list)

        stats_list=[]
        report= defaultdict(int)
        cnt += 1
        if cnt == 10:
          res=sorted(topdickt.items(), key=lambda item:item[1])
          print("%-10s %-10s %-15s"%("pid", "iops", "comm"))
          #for item in res:
          #  print("%s  %10dKB"%(item[0], item[1]*4))
          for item in res:
            try:
              command=open("/proc/"+str(item[0])+"/cmdline").read()
              print("%-10d %10dKB %-15s"%(item[0], item[1]*4, command[:-1]))
            except:
              continue;
          #  #print(item[0],item[1])
          print("Total write:%dKB\n"%(total_iops*4))
          exit(0)
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
