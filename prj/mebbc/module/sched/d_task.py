#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb
from time import sleep, strftime
from socket import inet_ntop, AF_INET, AF_INET6
from struct import pack
from collections import namedtuple, defaultdict
import argparse
import os
import time

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>    // for TASK_COMM_LEN

struct key_event_t {
    u32 pid;
    u64 data;
    int stack_id;
};

BPF_HASH(start, u64, u64);
BPF_HASH(block_time, int, u64);
BPF_STACK_TRACE(stack_traces, 2048);
BPF_PERF_OUTPUT(events_poll);

int oncpu(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid = prev->pid;
    u32 tgid = prev->tgid;
    u64 pid_tgid;
    u64 start_ts;
    u64 t = bpf_ktime_get_ns();
    int stack_id;
    u64  delta;

    if (FINISH_PID_A) {
        if (prev->state == TASK_UNINTERRUPTIBLE) {
          u64 t = bpf_ktime_get_ns();
          pid_tgid = pid + ((0UL + tgid)<<32);
          start.update(&pid_tgid, &t);
          return 0;
        }
    }

    pid_tgid = bpf_get_current_pid_tgid();

    u64 *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    start_ts = *start_ns;
    start.delete(&pid_tgid);

    if (FINISH_PID_B)
        return 0;
    

    delta = t - start_ts;
    stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
    block_time.increment(stack_id, delta);

    return 0; 
}
"""

examples = """examples:
    -pid  pid
"""

parser = argparse.ArgumentParser(
    description="Trace lock sched latency",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)

parser.add_argument("-p", "--pid", type=int, dest="pid",
    help="specify pid")

parser.add_argument("-i", "--interval", type=int, dest="interval",
    default=1, help="specify interval")

args = parser.parse_args()
if args.pid:
    bpf_text = bpf_text.replace("FILTER_PID", "pid_tgid >> 32 != %d"%args.pid)
    bpf_text = bpf_text.replace("FINISH_PID_A", "tgid == %d"%args.pid)
    bpf_text = bpf_text.replace("FINISH_PID_B", "tgid != %d"%args.pid)
else:
    bpf_text = bpf_text.replace("FILTER_PID", "0")
    bpf_text = bpf_text.replace("FINISH_PID_A", "1")
    bpf_text = bpf_text.replace("FINISH_PID_B", "0")

# load BPF program
b = BPF(text=bpf_text)
#b.attach_kprobe(event="io_schedule_timeout", fn_name="trace_io_schedule_timeout")
#b.attach_kprobe(event="io_schedule", fn_name="trace_io_schedule")
#b.attach_kretprobe(event="io_schedule", fn_name="rettrace_io_schedule")
#b.attach_kretprobe(event="io_schedule_timeout", fn_name="rettrace_io_schedule_timeout")

b.attach_kprobe(event="finish_task_switch", fn_name="oncpu")

label = "msecs"
exiting = 0
stack_traces = b.get_table("stack_traces")

block_time = b["block_time"]
print("start trace\n")
while (1):
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    for k, v in block_time.items():
      print("total ts:%d\n"%v.value)
      stack_id = int(k.value)
      if stack_id >= 0:
        kernel_stack = stack_traces.walk(k.value)
        for addr in kernel_stack:
           printb(b"   %s" % (b.ksym(addr)))
    block_time.clear()
    if exiting:
        exit()
