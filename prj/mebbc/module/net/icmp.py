#!/usr/bin/python
from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
from socket import inet_ntop, AF_INET, AF_INET6
from struct import pack
from collections import namedtuple, defaultdict
import argparse
import os
import time

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/list.h>
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <linux/socket.h>
#include <linux/tcp.h>
#include <net/sock.h>
#include <net/route.h>
#include <linux/icmp.h>
#include <bcc/proto.h>

struct key_event_t {
    u32 saddr;
    u32 daddr;
    u32 type;
    u32 code;
    u32 mtu;
};
BPF_PERF_OUTPUT(events_poll);
int trace_hook_func(struct pt_regs *ctx)
{
    struct sk_buff *skb = (struct sk_buff *)ctx->di;
    struct iphdr *iphdr = (struct iphdr *)skb->data;
    struct icmphdr *icmph = (struct icmphdr *)(skb->head + skb->transport_header);
    u16 mtu;


    struct key_event_t data_key = {};

#if 0
    __builtin_memcpy(&data_key.saddr, iphdr->saddr, sizeof(data_key.saddr));
    __builtin_memcpy(&data_key.daddr, iphdr->daddr, sizeof(data_key.daddr));
#else
    data_key.saddr = iphdr->saddr;
    data_key.daddr = iphdr->daddr;
    data_key.type  = icmph->type;
    data_key.code  = icmph->code;
    mtu  = icmph->un.frag.mtu;
    data_key.mtu  = ntohs(mtu);

#endif

    events_poll.perf_submit(ctx, &data_key, sizeof(data_key));
    return 0;
}
"""

# load BPF program
b = BPF(text=bpf_text)
b.attach_kprobe(event="icmp_unreach", fn_name="trace_hook_func")

label = "msecs"
exiting = 0

def print_event(cpu, data, size):
    event = b["events_poll"].event(data)
    print("%s %s %d %d %d" % 
        (inet_ntop(AF_INET, pack('I',event.saddr))
        ,inet_ntop(AF_INET, pack('I',event.daddr))
        ,event.type ,event.code, event.mtu
        ))

b["events_poll"].open_perf_buffer(print_event)
print("start trace...\n")
while (1):
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        exit()

