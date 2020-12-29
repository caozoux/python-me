#!/usr/bin/python
#
# bitehist.py	Block I/O size histogram.
#		For Linux, uses BCC, eBPF. Embedded C.
#
# Written as a basic example of using histograms to show a distribution.
#
# A Ctrl-C will print the gathered histogram then exit.
#
# Copyright (c) 2015 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 15-Aug-2015	Brendan Gregg	Created this.
# 03-Feb-2019   Xiaozhou Liu    added linear histogram.

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb
from time import sleep

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct key_t {
    int  w_k_stack_id;
    char waker[TASK_COMM_LEN];
    char target[TASK_COMM_LEN];
};

BPF_HASH(counts, struct key_t);
BPF_HISTOGRAM(dist);
BPF_HISTOGRAM(dist_linear);
BPF_STACK_TRACE(stack_traces, 1024);
int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
    struct key_t key = {};
    dist.increment(bpf_log2l(req->__data_len / 1024));
    key.wprintb(b"3    %-16x %s" % (addr, b.ksym(addr)))printb(b"4    %-16s %s" % (b"waker:", k.waker))printb(b"4    %-16s %s" % (b"waker:", k.waker))_k_stack_id = stack_traces.get_stackid(ctx, BPF_F_REUSE_STACKID);
    counts.increment(key, 0);
    return 0;
}
""")

# header
print("Tracing... Hit Ctrl-C to end.")

exiting=0
dist = b.get_table("dist")
stack_traces = b.get_table("stack_traces")
while 1:
# trace until Ctrl-C
    try:
            sleep(1)
    except KeyboardInterrupt:
            exiting = 1
            print()

    counts = b.get_table("counts")
    if exiting == 1:
        exit()
    for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
        waker_kernel_stack = [] if k.w_k_stack_id < 1 else \
            reversed(list(stack_traces.walk(k.w_k_stack_id))[1:])
        printb(b"2    %-16s %s" % (b"target:", k.target))
        for addr in waker_kernel_stack:
            printb(b"3    %-16x %s" % (addr, b.ksym(addr)))
        printb(b"4    %-16s %s" % (b"waker:", k.waker))
        print("5        %d\n" % v.value)
    counts.clear()
# output
    #print("log2 histogram")
    #print("~~~~~~~~~~~~~~")
    #b["dist"].print_log2_hist("kbytes")
    dist.print_log2_hist("cnt", "disk")
    dist.clear()
    #stack_traces.print_log2_hist()

    #waker_kernel_stack = reversed(list(stack_traces.walk(74))[1:])

    #for addr in waker_kernel_stack:
    #    printb(b"3    %-16x %s" % (addr, b.ksym(addr)))


#print("\nlinear histogram")
#print("~~~~~~~~~~~~~~~~")
#b["dist_linear"].print_linear_hist("kbytes")

