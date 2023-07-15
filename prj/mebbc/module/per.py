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
BPF_HASH(timeoutpid, u32, struct taskkey);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_PERF_OUTPUT(events);

int trace_mutex_lock(struct pt_regs *ctx, struct cgroup *dst_cgrp,
   const char *path, struct task_struct *task, bool threadgroup)
{
    struct taskkey key = {};
    u64 ts = bpf_ktime_get_ns();
    u32 pid = bpf_get_current_pid_tgid();

    if (ctx->di != LOCK)
      return 0;

    if (DEBUG)
        bpf_trace_printk("lock");
    ts &= ~(0xfUL);
    key.pid = pid;
    key.start_ns = ts;
    key.end_ns = 0;
    key.delta = ts;
    key.kernel_stack_id = 0;

    //bpf_get_current_comm(key.comm, 16);
    taskpid.update(&pid, &key);


    return 0;
}

int trace_mutex_unlock(struct pt_regs *ctx) {
    struct taskkey *key;
    u64 ts, delta;
    int per_key=0;
    u64 *value;
    u32 pid = bpf_get_current_pid_tgid();

    //bpf_get_current_comm(key.comm, 16);

    if (ctx->di != LOCK)
      return 0;

    key = taskpid.lookup(&pid);
    if (key == 0)
        return 0;

    ts = bpf_ktime_get_ns();
    delta = ts - key->start_ns;

    if (delta > 10000000) {
        key->delta = delta;
        key->end_ns = ts;
        key->kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
        timeoutpid.update(&pid, key);

        //struct data_t data = {};
        //data.pid = pid;
        //data.start_ns = ts;
        //events.perf_submit(ctx, &data, sizeof(data));
     }

    taskpid.delete(&pid);

    return 0;
}

TRACEPOINT_PROBE(sched, sched_switch)
{
    struct taskkey *key;
    u64 ts, *value, delta;
    u32 pid;

    pid = args->prev_pid;
    key = taskpid.lookup(&pid);
    if (key && (key->delta &1)) {
        struct data_t data = {};
        data.pid = pid;
        data.start_ns = bpf_ktime_get_ns();
        data.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)args, 0);
        events.perf_submit(args, &data, sizeof(data));
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
          struct data_t data = {};
          data.pid = pid;
          data.start_ns = bpf_ktime_get_ns();
          data.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)args, 0);
          events.perf_submit(args, &data, sizeof(data));
        }
    }

    return 0;
}

"""

bpf_text = bpf_text.replace('DEBUG', '0')
bpf_text = bpf_text.replace('LOCK', '0xffffffffb4a4f1c0')
b = BPF(text=bpf_text)
b.attach_kprobe(event="mutex_lock", fn_name="trace_mutex_lock")
b.attach_kprobe(event="mutex_unlock", fn_name="trace_mutex_unlock")

exiting = 0

stack_traces = b.get_table("stack_traces")
timeoutpid = b.get_table("timeoutpid")
perftimeoutpid=[]
recorddata=[]

def print_event(cpu, data, size):
    event = b["events"].event(data)
    recorddata.append(event)
    #print("%-8s %-6s %14s" % (strftime("%H:%M:%S"), event.pid, event.start_ns))
    #for item in perftimeoutpid:
    #  if item.pid == event.pid:
    #    if int(event.start_ns) >= item.start_ns and   int(event.start_ns) <= item.end_ns:
    #      print("%-8s %-6s %14s" % (strftime("%H:%M:%S"), event.pid, event.start_ns - item.start_ns))
          #kernel_stack = stack_traces.walk(int(event.kernel_stack_id))
          #print("find", event.kernel_stack_id)
          #for addr in kernel_stack:
          #  print("    %-16x %s" % (addr, b.ksym(addr)))

b["events"].open_perf_buffer(print_event, page_cnt=64)
while 1:
    try:
        sleep(1)
        exiting = 1
    except KeyboardInterrupt:
        exiting = 1

    #if 1:
    #  has_timeout = 0;
    #  for k in timeoutpid.keys():
    #      print("total delay us: %ld"%(int(timeoutpid[k].delta)/1000))
    #      if (int(timeoutpid[k].kernel_stack_id) != 0):
    #        kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id)
    #        for addr in kernel_stack:
    #          print("    %-16x %s" % (addr, b.ksym(addr)))
    #      has_timeout += 1
    #      perftimeoutpid.append(timeoutpid[k]);

    #if has_timeout:
    #    b.perf_buffer_poll(10)
    b.perf_buffer_poll(10)

    #timeoutpid.clear()
    #stack_traces.clear()
    if exiting:
      for k in timeoutpid.keys():
          print("total delay us: %ld  %ld-%ld"%(int(timeoutpid[k].delta)/1000, timeoutpid[k].start_ns, timeoutpid[k].end_ns))
          if (int(timeoutpid[k].kernel_stack_id) != 0):
            kernel_stack = stack_traces.walk(timeoutpid[k].kernel_stack_id)
            for addr in kernel_stack:
              print("    %-16x %s" % (addr, b.ksym(addr)))
            item = timeoutpid[k]
            pid=timeoutpid[k].pid
            last_ts = item.start_ns;
            for event in recorddata:
              if event.pid == item.pid:
                if int(event.start_ns) >= item.start_ns and   int(event.start_ns) <= item.end_ns:
                  print("find:%d %ld "%(event.pid, event.start_ns - last_ts))
                  last_ts = event.start_ns
                  if event.kernel_stack_id != 0:
                    kernel_stack = stack_traces.walk(int(event.kernel_stack_id))
                    for addr in kernel_stack:
                      print("    %-16x %s" % (addr, b.ksym(addr)))
            #exit(0)
         
      exit(1)
