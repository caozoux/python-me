#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

from socket import inet_ntop, ntohs, AF_INET, AF_INET6
from struct import pack
from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <linux/mm.h>
#include <linux/tcp.h>

typedef struct {
    u32 snd_wnd;
    u32 snd_una;
    u32 snd_wl1;
    u32 rcv_nxt;
    u32 saddr;
    u32 daddr;
    u16 lport;
    u16 dport;
} key_data;

BPF_HASH(data_hash, key_data);

int kprobe_tcp_sendmsg_locked(struct pt_regs *ctx) {
    struct sock *skp = (struct sock *)ctx->di;
    struct tcp_sock *tp = (struct tcp_sock *)ctx->di;
    key_data key = {};

    key.saddr = skp->__sk_common.skc_rcv_saddr;
    key.daddr = skp->__sk_common.skc_daddr;
    key.lport = skp->__sk_common.skc_num;
    key.dport = skp->__sk_common.skc_dport;

    key.snd_wnd  = tp->snd_wnd;
    key.snd_una  = tp->snd_una;
    key.snd_wl1  = tp->snd_wl1;
    key.rcv_nxt = tp->rcv_nxt;
    data_hash.atomic_increment(key);

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
b.attach_kprobe(event="tcp_sendmsg_locked", fn_name="kprobe_tcp_sendmsg_locked")

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
        printb(b"%s:%-6d %s:%-6d %ld %ld %ld"% (
            inet_ntop(AF_INET, pack("I", item.saddr)).encode(), item.lport,
            inet_ntop(AF_INET, pack("I", item.daddr)).encode(), item.dport,
            item.snd_wnd, item.snd_una, item.snd_wl1))

    data_key.clear()
    if exiting:
        exit(1)

