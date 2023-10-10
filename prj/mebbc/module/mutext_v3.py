!#!/usr/bin/python3
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
    int kernel_stack_id;
};

struct data_t {
    u32 pid;
    u64 delta_us;
    int kernel_stack_id;
};

struct mutex_lock_key{
    u32 pid;
    u64 delta_s;
    u64 delta_e;
};

BPF_HASH(taskstack, struct taskstackkey);
BPF_HASH(mutex_start_pid, u32, struct mutex_lock_key);
BPF_HASH(timeoutpid, u32, struct taskkey);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_PERF_OUTPUT(events);

static u32 trace_pid = 0;
static u32 trace_pid_pend = 0;
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
    taskpid.update(&pid, &key);
    trace_pid = pid;
    trace_pid_pend = 0;

    return 0;
}

int trace_mutex_lock_ret(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid();
    if (trace_pid == pid)

    return 0;
}

int trace_mutex_unlock(struct pt_regs *ctx) {
    struct taskkey *key;
    u64 *ts, delta;
    int per_key=0;
    u64 *value;
    u32 pid = bpf_get_current_pid_tgid();

    //bpf_get_current_comm(key.comm, 16);

    if (ctx->di != LOCK)
      return 0;

    key = taskpid.lookup(&pid);
    if (key == 0)
        return 0;

    delta = bpf_ktime_get_ns() - key->delta;

    if (delta > 100000000) {
        key->delta = delta;
        key->kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
        timeoutpid.update(&pid, key);
     }

    taskpid.delete(&pid);

    return 0;
}

TRACEPOINT_PROBE(sched, sched_switch)
{
    struct taskkey *key;
    u64 *ts, *value, delta;
    u32 pid;

    pid = args->prev_pid;
    key = taskpid.lookup(&pid);
    if (key && (key->delta &1)) {
        delta = bpf_ktime_get_ns() - key->delta;
        int offset = key->offset;
        if (key->offset < 4 ) {
            if (key->offset == 0) {
                key->delta1 = delta;
                key->kernel_stack_id0 = stack_traces.get_stackid((struct pt_regs *)args, 0);
            } else if (key->offset == 1) {
                key->delta2 = delta;
                key->kernel_stack_id1 = stack_traces.get_stackid((struct pt_regs *)args, 0);
            } else if (key->offset == 2) {
                key->delta3 = delta;
                key->kernel_stack_id2 = stack_traces.get_stackid((struct pt_regs *)args, 0);
            } else if (key->offset == 4) {
                key->delta4 = delta;
                key->kernel_stack_id3 = stack_traces.get_stackid((struct pt_regs *)args, 0);
            } 
            key->offset += 1;
        }
    }

    pid = args->next_pid;
    key = taskpid.lookup(&pid);
    if (key) {
        if (!(key->delta &0xf)) {
          delta = bpf_ktime_get_ns();
          delta &= ~(15UL);
          delta += 1;
          key->delta = delta;
          taskpid.update(&pid, key);
          if (DEBUG)
              bpf_trace_printk("switch n %ld %ld", pid, delta);
        } else {
          delta = bpf_ktime_get_ns() - key->delta;
          int offset = key->offset;
          if (key->offset < 4 ) {
              if (key->offset == 0) {
                  key->delta1 = delta;
                  key->kernel_stack_id0 = stack_traces.get_stackid((struct pt_regs *)args, 0);
              } else if (key->offset == 1) {
                  key->delta2 = delta;
                  key->kernel_stack_id1 = stack_traces.get_stackid((struct pt_regs *)args, 0);
              } else if (key->offset == 2) {
                  key->delta3 = delta;
                  key->kernel_stack_id2 = stack_traces.get_stackid((struct pt_regs *)args, 0);
              } else if (key->offset == 4) {
                  key->delta4 = delta;
                  key->kernel_stack_id3 = stack_traces.get_stackid((struct pt_regs *)args, 0);
              } 
              key->offset += 1;
          }
        }
    }

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

    if 1:
      for k in timeoutpid.keys():
          print("total delay us: %ld"%(int(timeoutpid[k].delta)/1000))
          if (int(timeoutpid[k].kernel_stack_id) != 0):
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))
           
          if (timeoutpid[k].kernel_stack_id0 != 0):
            print("sub delay us: %ld"%(int(timeoutpid[k].delta1)/1000))
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id0)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))
          if (timeoutpid[k].kernel_stack_id1 != 0):
            print("sub delay us: %ld"%(int(timeoutpid[k].delta2)/1000))
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id1)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))
          if (timeoutpid[k].kernel_stack_id2 != 0):
            print("sub delay us: %ld"%(int(timeoutpid[k].delta3)/1000))
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id2)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))
          if (timeoutpid[k].kernel_stack_id3 != 0):
            print("sub delay us: %ld"%(int(timeoutpid[k].delta4)/1000))
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id3)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))
    timeoutpid.clear()
    stack_traces.clear()
    if exiting:
        exit(1)
