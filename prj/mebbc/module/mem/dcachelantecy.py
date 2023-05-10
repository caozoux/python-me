#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/dcache.h>

BPF_HASH(start, struct dentry*);
BPF_HISTOGRAM(dist);

// time block I/O
int bpf___dentry_kill(struct pt_regs *ctx)
{
    struct dentry *dentry=  (struct dentry*)ctx->di;

    u64 ts = bpf_ktime_get_ns();
    //bpf_trace_printk("s %lx\\n", dentry);
    start.update(&dentry, &ts);
    return 0;
}

// output
int bpf___d_free(struct pt_regs *ctx)
{
    u64 *tsp, delta;
    struct rcu_head *head = (struct rcu_head *) ctx->di;

    struct dentry *dentry = (struct dentry *) ((void*)head - 0xb0);

    //bpf_trace_printk("f %lx %lx\\n", dentry, head);
    // fetch timestamp and calculate delta
    tsp = start.lookup(&dentry);
    if (tsp == 0) {
        return 0;   // missed issue
    }
    delta = bpf_ktime_get_ns() - *tsp;
    delta /= 1000000;

    start.delete(&dentry);
    //dist.atomic_increment(bpf_log2l(delta));
    dist.increment(bpf_log2l(delta));
    return 0;
}
"""

# load BPF program
b = BPF(text=bpf_text)
b.attach_kprobe(event="__dentry_kill", fn_name="bpf___dentry_kill")
b.attach_kprobe(event="__d_free", fn_name="bpf___d_free")
exiting = 0
dist = b.get_table("dist")
label = "msecs"
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
    dist.print_log2_hist(label, "disk")
    dist.clear()

    if exiting:
        exit(1)
