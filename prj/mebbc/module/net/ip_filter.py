#!/usr/bin/python3

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <uapi/linux/ptrace.h>
//#include <linux/skbuff.h>
#include <net/sock.h>
#include <net/tcp_states.h>
#include <bcc/proto.h>

typedef struct {
    u64 pid;
    char comm[16];
    u64 ts;
} key_data;

BPF_HASH(data_hash, key_data);

int ip_rcv_func(struct pt_regs *ctx)
{
    //struct iphdr *iph;
    //struct sk_buff *skb;

    //skb = (struct sk_buff *) ctx->di;
    //iph = (struct iphdr *)skb->head + skb->network_header;
    //bpf_trace_printk("%d\\n",iph->ihl);

    return 0;
}

"""

examples = """examples:
    -i  interval milliseconds
"""

parser = argparse.ArgumentParser(
    description="Trace lock sched latency",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)

parser.add_argument("-", "--interval", type=int, dest="interval",
    help="summary interval, in seconds")

args = parser.parse_args()

b = BPF(text=bpf_text)
b.attach_kprobe(event="ip_rcv", fn_name="ip_rcv_func")

data_key = b.get_table("data_hash")
interval = 1
exiting = 0

if args.interval:
    interval = args.interval

print("start trace..\n")
while 1:
    try:
        sleep(interval)
    except KeyboardInterrupt:
        exiting = 1

    for item in data_key.keys():
        print("comm:%s pid:%x latency:%ld"%(item.comm, item.pid, item.ts))

    data_key.clear()
    if exiting:
        exit(1)

