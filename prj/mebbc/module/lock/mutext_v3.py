#!/usr/bin/python3
from __future__ import print_function
from bpfcc import BPF
from time import sleep, strftime

import argparse
import curses
import pwd
import re
import signal
from time import sleep

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>
#include <linux/fs.h>
#include <linux/cgroup-defs.h>

struct taskstackkey {
    u64 delta;
    //0: start 1:switch in 2:switch_out 3:end
    int type;
    int kernel_stack_id;
};

struct data_t {
    u32 pid;
    u64 delta_us;
    int kernel_stack_id;
};

struct mutex_lock_key {
    u32 pid;
    u64 delta_s;
    u64 delta_e;
};

BPF_HASH(task_switch, u64, struct taskstackkey);
BPF_HASH(mutex_start_pid, u32, struct mutex_lock_key);
BPF_HASH(timeoutpid, u32, struct taskkey);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_PERF_OUTPUT(events);

static u32 trace_pid = 0;
static u32 trace_pid_pend = 0;
static u64 trace_pid_ts = 0;
int trace_mutex_lock(struct pt_regs *ctx)
{
    struct mutex_lock_key key = {};
    u64 ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid();

    if (ctx->di != LOCK)
      return 0;

    if (DEBUG)
        bpf_trace_printk("lock");

    key.pid = pid;
    key.delta_s = ts;
    key.delta_e = 0;
    mutex_start_pid.update(&pid, &key);
    trace_pid = pid;
    trace_pid_pend = 0;

    return 0;
}

int trace_mutex_lock_ret(struct pt_regs *ctx)
{
    struct mutex_lock_key *key;
    u32 pid = bpf_get_current_pid_tgid();
    key = taskpid.lookup(&pid);
    if (key == 0)
        return 0;

    mutex_start_pid.delete(&pid);

    if (trace_pid != 0)
        return 0;

    trace_pid_pend = pid;
    trace_pid_ts = ts;

    struct taskstackkey stack_key;
    u64 ts = bpf_ktime_get_ns();
    stack_key.delta = ts;
    stack_key.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);

    task_switch.update(&ts, &stack_key);

    return 0;
}

int trace_mutex_unlock(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid();

    if (pid != trace_pid)
        return 0;

    u64 ts = bpf_ktime_get_ns();

    delta = ts - trace_pid_ts;

    if (delta > 2000000000) {
         bpf_trace_printk("switch n %ld %ld", pid, delta);
    }
    trace_pid = 0;
    return 0;
}

"""

bpf_text = bpf_text.replace('DEBUG', '0')
bpf_text = bpf_text.replace('LOCK', '0xffffffffb4a4f1c0')
b = BPF(text=bpf_text)
b.attach_kprobe(event="mutex_lock", fn_name="trace_mutex_lock")
b.attach_kretprobe(event="mutex_lock", fn_name="trace_mutex_lock_ret")
b.attach_kprobe(event="mutex_unlock", fn_name="trace_mutex_unlock")

exiting = 0

stack_traces = b.get_table("stack_traces")
timeoutpid = b.get_table("timeoutpid")

while 1:
    try:
        sleep(2)
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        exit(1)
