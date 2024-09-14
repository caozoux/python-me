#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
# Do not import unicode_literals until #623 is fixed
# from __future__ import unicode_literals
from __future__ import print_function

from bcc import BPF
from collections import defaultdict
from time import strftime

import argparse
import curses
import pwd
import re
import signal
from time import sleep

bpf_text = """
BPF_HASH(counts, struct key_t);
#include <linux/memcontrol.h>
#include <linux/mm.h>
#include <linux/fs.h>
#include <uapi/linux/ptrace.h>

BPF_HASH(start, struct mem_cgroup *);
int __memcg_kmem_uncharge_memcg(struct pt_regs *ctx)
{
    struct page *page = ctx->di;
    int order = (int)ctx->dx;
    struct mem_cgroup *memcg =  (struct mem_cgroup *)ctx->rcx;

    start.increment(&memcg, order);
    return 0;
}

int __memcg_kmem_charge_memcg(struct pt_regs *ctx) 
{
    int order = (int)ctx->sx;
    struct mem_cgroup *memcg =  (struct mem_cgroup *)ctx->di;

    start.increment(&memcg, -order);

    return 0;
}

"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="account_page_dirtied", fn_name="do_count")
counts = b.get_table("counts")

exiting = 0
stats = defaultdict(lambda: defaultdict(int))
report= defaultdict(int)
stats_list = []
cnt=0
while 1:
