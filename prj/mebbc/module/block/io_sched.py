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

struct task_partern {
   char data[0x948];
   u64  flags;
};

struct task_bits {
#if 1
    unsigned int in_execve : 1;
    unsigned int in_iowait : 1;
    unsigned int restore_sigmask : 1;
    unsigned int in_user_fault : 1;
    unsigned int rh_reserved_memcg_kmem_skip_account : 1;
    unsigned int no_cgroup_migration : 1;
    unsigned int use_memdelay : 1;
    unsigned int frozen : 1;
    int data;
#else
    u64 data;
#endif
};

BPF_HASH(start, u64, u64);
BPF_STACK_TRACE(stack_traces, 2048);
BPF_PERF_OUTPUT(events_poll);

static int io_sched_end(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 t = bpf_ktime_get_ns();
    u64 start_ts;

    if (FILTER_PID)
        return 0;

    u64 *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;
    start_ts = *start_ns;
    start.delete(&pid_tgid);

    struct key_event_t data_key = {};
    data_key.data = t - start_ts;
    data_key.pid = pid_tgid;
    data_key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
    events_poll.perf_submit(ctx, &data_key, sizeof(data_key));

    return 0;
}

static int io_sched_start(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 t = bpf_ktime_get_ns();

    if (FILTER_PID)
        return 0;

    start.update(&pid_tgid, &t);

    return 0;
}

int trace_io_schedule(struct pt_regs *ctx)
{
    return io_sched_start(ctx);
}

int trace_io_schedule_timeout(struct pt_regs *ctx)
{
    return io_sched_start(ctx);
}

int rettrace_io_schedule(struct pt_regs *ctx)
{
    return io_sched_end(ctx);
}

int rettrace_io_schedule_timeout(struct pt_regs *ctx)
{
    return io_sched_end(ctx);
}

int oncpu(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid = prev->pid;
    u32 tgid = prev->tgid;
    u64 pid_tgid;
    u64 start_ts;
    u64 t = bpf_ktime_get_ns();
    struct task_bits task_data;

    if (FINISH_PID_A) {
        bpf_probe_read_kernel(&task_data, sizeof(struct task_bits), &(((struct task_partern *)prev)->flags));
        if (task_data.in_iowait) {
          u64 t = bpf_ktime_get_ns();
          pid_tgid = pid + ((0UL + tgid)<<32);
          start.update(&pid_tgid, &t);
          return 0;
        }
    }

    pid = bpf_get_current_pid_tgid();
    tgid = bpf_get_current_pid_tgid() >> 32;
    //pid_tgid = pid + ((0UL + tgid)<<32);
    pid_tgid =   bpf_get_current_pid_tgid();

    u64 *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    if (FINISH_PID_B)
        return 0;
    
    start_ts = *start_ns;
    start.delete(&pid_tgid);

    struct key_event_t data_key = {};
    data_key.data = t - start_ts;
    data_key.pid = pid_tgid;
    data_key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
    events_poll.perf_submit(ctx, &data_key, sizeof(data_key));
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

def print_event(cpu, data, size):
    event = b["events_poll"].event(data)
    #print("tgid:%d pid:%d io_sched(ns):%ld\n"%(args.pid, event.pid, event.data))
    print("pid: %d delta: %d"%(event.pid, event.data))
    kernel_stack = stack_traces.walk(event.stack_id)
    for addr in kernel_stack:
       printb(b"   %s" % (b.ksym(addr)))

b["events_poll"].open_perf_buffer(print_event)
print("start trace\n")
while (1):
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        exit()
