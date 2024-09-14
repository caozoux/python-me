#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
# Do not import unicode_literals until #623 is fixed
# from __future__ import unicode_literals
from __future__ import print_function

from bcc import BPF
from bcc.utils import printb
from collections import defaultdict
from time import strftime

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
    u32 pid;
    int kernel_stack_id;
};
struct taskkey {
    u32 pid;
    char comm[16];
};

//BPF_HASH(taskpid, u64, u64);
BPF_HASH(taskstack, struct taskstackkey);
BPF_HASH(taskpid, struct taskkey);
BPF_HASH(csspointer, u64, u64);
BPF_HISTOGRAM(csstask, struct task_struct *);
BPF_STACK_TRACE(stack_traces, 1024);

int kprobe_put_task_struct(struct pt_regs *ctx) {
    struct task_struct *task = (struct task_struct *)ctx->di;
    struct taskkey key;
    u64 *count;

    key.pid = task->pid;
    bpf_probe_read_kernel(&key.comm, sizeof(key.comm), task->comm);
    count = taskpid.lookup(&key);
    if (count) {
      bpf_trace_printk("%d %s\\n", key.pid, key.comm);
    }
    return 0;
}

int kretprobe_blkcg_css_alloc(struct pt_regs *ctx)
{
    u64 css = (u64)ctx->ax;
    u64 *count, one = 1;
    count = csspointer.lookup(&css);
    if (!count) {
        csspointer.update(&css, &one);
    } else {
        *count += 1;
    }
    return 0;
}

int kprobe_blkcg_css_free(struct pt_regs *ctx) {
    u64 css = (u64)ctx->di;
    u64 *count, one = 0;
    count = csspointer.lookup(&css);
    if (count) {
        *count -= 1;
    }
    return 0;
}

int trace_cgroup_attach_task(struct pt_regs *ctx, struct cgroup *dst_cgrp,
   const char *path, struct task_struct *task, bool threadgroup)
{
    //csstask.update(&task, 1);
    csstask.increment(task);
    return 0;
}

TRACEPOINT_PROBE(cgroup, cgroup_css_get) 
{
    struct taskkey key;
    u64 css = (u64)args->caddr;
    u64 *count, one = 1;
    count = csspointer.lookup(&css);
    if (count) {
        key.pid = bpf_get_current_pid_tgid()>>32;
        bpf_get_current_comm(key.comm, 16);
        count = taskpid.lookup(&key);
        if (!count) {
            taskpid.update(&key, &one);
        } else {
            *count += 1;
        }
    }

    count = csspointer.lookup(&css);
    if (count) {
        *count += 1;
    }
    return 0;
}

//int trace_cgroup_css_put(struct pt_regs *ctx, struct cgroup_subsys_state *css, unsigned int n, bool istr)
TRACEPOINT_PROBE(cgroup, cgroup_css_put) 
{
    u64 css = (u64)args->caddr;
    u64 *count, one = 1;
    struct taskkey key;
    count = csspointer.lookup(&css);
    if (count) {

        *count -= 1;

        key.pid = bpf_get_current_pid_tgid()>>32;
        bpf_get_current_comm(key.comm, 16);

        count = taskpid.lookup(&key);
        if (count) {
            *count -= 1;
        } else {
          struct taskstackkey stackkey;
          stackkey.pid = bpf_get_current_pid_tgid()>>32;
          stackkey.kernel_stack_id = stack_traces.get_stackid((struct pt_regs *)args, 0);
          bpf_trace_printk("%d %s\\n", key.pid, key.comm);
          taskstack.increment(stackkey);
        }
    } 

    return 0;
}

"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="__put_task_struct", fn_name="kprobe_put_task_struct")
b.attach_kprobe(event="blkcg_css_free", fn_name="kprobe_blkcg_css_free")
b.attach_kretprobe(event="blkcg_css_alloc", fn_name="kretprobe_blkcg_css_alloc")
b.attach_kprobe(event="cgroup_attach_task", fn_name="trace_cgroup_attach_task")
#b.attach_tracepoint(event="cgroup_css_get", fn_name="trace_cgroup_css_get")
#b.attach_kprobe(event="cgroup_css_put", fn_name="trace_cgroup_css_put")


exiting = 0

csspointer = b.get_table("csspointer")
stack_traces = b.get_table("stack_traces")
taskstack = b.get_table("taskstack")
taskpid = b.get_table("taskpid")
while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        print("");
        for key in csspointer.keys():
          print("%lx %d\n"%(key.value, csspointer[key].value))
        print("task pid");
        for key in taskpid.keys():
          print("%ld %s %lx"%(key.pid, key.comm, taskpid[key].value))

        for k, v in sorted(taskstack.items(),
                           key=lambda taskstack: taskstack[1].value):
            kernel_stack = stack_traces.walk(k.kernel_stack_id)
            for addr in kernel_stack:
                printb(b"    %-16x %s" % (addr, b.ksym(addr)))
            print("    %d\n" % v.value)

        exit(1)
