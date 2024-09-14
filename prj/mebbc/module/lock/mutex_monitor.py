#!/usr/bin/python3
from __future__ import print_function
from bpfcc import BPF
from time import sleep, strftime

import argparse
import curses
import pwd
import re
import os
import signal
from time import sleep

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>
#include <linux/fs.h>
#include <linux/cgroup-defs.h>

#define MAX_SIZE (8)
struct taskstackkey {
    u64 delta;
    int kernel_stack_id;
};

struct data_t {
    u32 pid;
    u64 start_ns;
    int kernel_stack_id;
};

struct taskkey {
    u32 pid;
    u64 start_ns;
    u64 end_ns;
    u64 delta;
    int kernel_stack_id;
};

BPF_HASH(taskstack, struct taskstackkey);
BPF_HASH(taskpid, u32, struct taskkey);
BPF_HASH(rettaskpid, u32, u64);
BPF_HASH(timeoutpid, u32, struct taskkey);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_PERF_OUTPUT(events);

int rettrace_mutex_lock(struct pt_regs *ctx)
{
    u64 ts;
    u32 pid = bpf_get_current_pid_tgid();
    u64 *spid;

    spid = rettaskpid.lookup(&pid);
    if (spid == 0)
      return 0;

    if (DEBUG)
        bpf_trace_printk("retlock");
    rettaskpid.delete(&pid);

    struct taskkey key = {};

    ts = bpf_ktime_get_ns();
    key.pid = pid;
    key.start_ns = ts;
    key.end_ns = 0;
    ts &= ~(0x1UL);
    key.delta = ts;
    key.kernel_stack_id = 0;

    //bpf_get_current_comm(key.comm, 16);
    taskpid.update(&pid, &key);


    return 0;
}
int trace_mutex_lock(struct pt_regs *ctx, struct cgroup *dst_cgrp,
   const char *path, struct task_struct *task, bool threadgroup)
{
    u64 ts;
    u32 pid = bpf_get_current_pid_tgid();

    if (ctx->di != LOCK)
      return 0;

    if (DEBUG)
        bpf_trace_printk("lock");

    if (KRETPROBE_ENABLE)
    {
      ts = bpf_ktime_get_ns();

      //bpf_get_current_comm(key.comm, 16);
      rettaskpid.update(&pid, &ts);
    } else {
      struct taskkey key = {};
      ts = bpf_ktime_get_ns();
      key.pid = pid;
      key.start_ns = ts;
      key.end_ns = 0;
      ts &= ~(0x1UL);
      key.delta = ts;
      key.kernel_stack_id = 0;

      //bpf_get_current_comm(key.comm, 16);
      taskpid.update(&pid, &key);
    }


    return 0;
}

int trace_mutex_unlock(struct pt_regs *ctx) {
    struct taskkey *key;
    u64 ts, delta;
    int per_key=0;
    u64 *value;
    u32 pid = bpf_get_current_pid_tgid();
    u32 tid = bpf_get_current_pid_tgid()>>32;

    //bpf_get_current_comm(key.comm, 16);

    if (FILTER_PID || FILTER_TGID)
      return 0;

    if (ctx->di != LOCK)
      return 0;

    key = taskpid.lookup(&pid);
    if (key == 0)
        return 0;

    ts = bpf_ktime_get_ns();
    delta = ts - key->start_ns;

    if (FILTER_US) {
        key->delta = delta;
        key->end_ns = ts;
        key->kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
        timeoutpid.update(&pid, key);
     }

    taskpid.delete(&pid);

    return 0;
}

TRACEPOINT_PROBE(sched, sched_switch)
{
    struct taskkey *key;
    u64 ts, *value, delta;
    u32 pid;

    if (SCHED_DISABLE)
      return 0;

    pid = args->prev_pid;
    key = taskpid.lookup(&pid);
    //if (key && (key->delta &1)) {
    if (key ) {
        struct data_t data = {};
        data.pid = pid;
        data.start_ns = bpf_ktime_get_ns();
        data.start_ns &= (~1UL);
        data.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)args, 0);
        events.perf_submit(args, &data, sizeof(data));
    }

    pid = args->next_pid;
    key = taskpid.lookup(&pid);
    if (key) {
        struct data_t data = {};
        data.pid = pid;
        data.start_ns = bpf_ktime_get_ns();
        data.start_ns |= 1;
        data.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)args, 0);
        events.perf_submit(args, &data, sizeof(data));
    }

    return 0;
}

"""

examples = """examples:
    ./locklantency               # trace lock latency higher than 100000 us (default)
    ./locklantency -l cgroup_mutext -i 1 10000    # trace cgroup_mutex lock latency higher than 1000 us
    ./locklantency -p 123        # trace pid 123
    ./locklantency -t 123        # trace tid 123 (use for threads only)
"""

lockname=""
disable_sched_trace=0
lock_kretprobe=1
parser = argparse.ArgumentParser(
    description="Trace lock latency",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("min_us", nargs="?", default='10000',
    help="minimum lock latency to trace, in us (default 10000)")
parser.add_argument("interval", nargs="?", default='1',
    help="interval monitor, default 1s)")

parser.add_argument("-p", "--pid", metavar="PID", dest="pid",
    help="trace this PID only", type=int)
parser.add_argument("-t", "--tid", metavar="TID", dest="tid",
    help="trace this TID only", type=int)
parser.add_argument("-i", "--interval", metavar="INTERVAL", dest="interval",
    help="interval monitor, default 1s", type=int)
parser.add_argument("-d", "--disable",  dest="disable", action="store_true",
    help="disable trace lock sched_switch calltrace")
parser.add_argument("-r", "--retdisable",  dest="retdisable", action="store_true",
    help="disable trace mutex_lock return hook")
parser.add_argument("-l", "--lockname", metavar="LOCAKNAME", dest="lockname",
    help="monitor mutex lock name", type=str)
args = parser.parse_args()

bpf_text = bpf_text.replace('DEBUG', '0')
min_us = int(args.min_us)
interval_s = 1

if args.tid:
    bpf_text = bpf_text.replace('FILTER_PID', 'pid != %s' % args.tid)
else:
    bpf_text = bpf_text.replace('FILTER_PID', '0')

if args.pid:
    bpf_text = bpf_text.replace('FILTER_TGID', 'tgid != %s' % args.pid)
else:
    bpf_text = bpf_text.replace('FILTER_TGID', '0')
if args.lockname:
    lockname=args.lockname
if args.disable:
    disable_sched_trace=1

if args.retdisable:
  lock_kretprobe=0

if not lockname:
  print("please specify lockname")
  exit(1)
else:
  #addr=BPF.ksymname(args.lockname)
  res=os.popen("cat /proc/kallsyms  | grep \" "+lockname+"$\"").readlines()
  if len(res) != 1:
    print("not find:", lockname, res);
    exit(1)
  addrstr="0x"
  addrstr +=res[0].split(" ")[0]
  bpf_text = bpf_text.replace('LOCK', addrstr)
  print("monitor lock addr",addrstr)

if disable_sched_trace:
  bpf_text = bpf_text.replace('SCHED_DISABLE', '1')
else:
  bpf_text = bpf_text.replace('SCHED_DISABLE', '0')

if lock_kretprobe:
    bpf_text = bpf_text.replace('KRETPROBE_ENABLE', '1')
else:
    bpf_text = bpf_text.replace('KRETPROBE_ENABLE', '0')

bpf_text = bpf_text.replace('FILTER_US', 'delta >=  %s' % str(min_us*1000))

b = BPF(text=bpf_text)
b.attach_kprobe(event="mutex_lock", fn_name="trace_mutex_lock")

if lock_kretprobe:
  b.attach_kretprobe(event="mutex_lock", fn_name="rettrace_mutex_lock")

b.attach_kprobe(event="mutex_unlock", fn_name="trace_mutex_unlock")

exiting = 0

stack_traces = b.get_table("stack_traces")
timeoutpid = b.get_table("timeoutpid")
perftimeoutpid=[]
recorddata=[]

def print_event(cpu, data, size):
    event = b["events"].event(data)
    recorddata.append(event)

b["events"].open_perf_buffer(print_event, page_cnt=64)
print("Tracing lock latency  higher than %d us interl %d s" % (min_us, interval_s))
while 1:
    try:
        sleep(interval_s)
    except KeyboardInterrupt:
        exiting = 1

    b.perf_buffer_poll(1)

    for k in timeoutpid.keys():
        print("total delay us: %ld  %ld-%ld"%(int(timeoutpid[k].delta)/1000, timeoutpid[k].start_ns, timeoutpid[k].end_ns))
        if (int(timeoutpid[k].kernel_stack_id) != 0):
          try:
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id)
            for addr in kernel_stack:
              print("    %-16x %s" % (addr, b.ksym(addr)))
          except Exception as e:
            print("Warning lost stack")
          item = timeoutpid[k]
          pid=timeoutpid[k].pid
          last_ts = item.start_ns;
          for event in recorddata:
            if event.pid == item.pid:
              if event.start_ns >= item.start_ns and  event.start_ns < item.end_ns:
                if event.start_ns & 1:
                  print("sub %d %ld us in"%(event.pid, (event.start_ns - last_ts)/1000))
                else:
                  print("sub %d %ld us out"%(event.pid, (event.start_ns - last_ts)/1000))
                last_ts = event.start_ns
                if event.kernel_stack_id != 0:
                  try:
                    kernel_stack = stack_traces.walk(int(event.kernel_stack_id))
                    for addr in kernel_stack:
                      print("    %-16x %s" % (addr, b.ksym(addr)))
                  except Exception as e:
                    print("Warning lost stack")
         
        recorddata.clear()
        timeoutpid.clear()
        stack_traces.clear()
    if exiting:
      exit(1)

