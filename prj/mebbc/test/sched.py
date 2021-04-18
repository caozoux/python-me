#!/usr/bin/python3
from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse


bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/sched.h>
#include </home/zc/github/linux/kernel/sched/sched.h>

void kprobe_enqueue_task_fair(struct rq *rq, struct task_struct *p, int flags)
{

    bpf_trace_printk("task:%s \\n", p->comm);
}

"""


# load BPF program
b = BPF(text=bpf_text)


exiting = 0
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1;
    if exiting == 1:
        exit(0);



