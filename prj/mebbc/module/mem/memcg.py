#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF
from time import sleep
import os

from collections import defaultdict

# load BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/memcontrol.h>

BPF_HASH(start, struct mem_cgroup *);
BPF_HASH(end, struct mem_cgroup *);
int bpf__memcg_kmem_charge_memcg(struct pt_regs *ctx)
{
    int order = (int)ctx->dx;
    struct mem_cgroup *memcg = (struct mem_cgroup *)ctx->cx;

    start.increment(memcg, 1<<order);
    return 0;
}

int bpf__memcg_kmem_uncharge_memcg(struct pt_regs *ctx)
{
    struct mem_cgroup *memcg = (struct mem_cgroup *)ctx->di;
    unsigned int nr_pages = (unsigned int )ctx->si;

    end.increment(memcg, nr_pages);
    return 0;
}
"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="__memcg_kmem_charge_memcg", fn_name="bpf__memcg_kmem_charge_memcg")
b.attach_kprobe(event="__memcg_kmem_uncharge_memcg", fn_name="bpf__memcg_kmem_uncharge_memcg")
# header
print("Tracing... Hit Ctrl-C to end.")

memcg_calculate = defaultdict(int)

start = b["start"]
end = b["end"]
exiting=0
# trace until Ctrl-C
while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting=1
        print()

    if exiting:
        for k, v in start.items():
            memcg_calculate[k.value] +=  v.value
        for k, v in end.items():
            memcg_calculate[k.value] -=  v.value

        for k, v in memcg_calculate.items():
            print("%lx:%d"%(k,v))
        exit(1)

