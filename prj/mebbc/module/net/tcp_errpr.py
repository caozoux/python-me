#!/usr/libexec/platform-python
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
#include <bcc/proto.h>


struct ipv4_key_t {
    u32 saddr;
    u32 daddr;
    u16 lport;
    u16 dport;
};

BPF_HASH(ipv4_send_bytes, struct ipv4_key_t);
// output
int trace_tcp_write_err(struct pt_regs *ctx)
{
    struct sock *sk = (struct sock *)ctx->di;
    u16 dport;
    struct ipv4_key_t ipv4_key = {};
    ipv4_key.saddr = sk->__sk_common.skc_rcv_saddr;
    ipv4_key.daddr = sk->__sk_common.skc_daddr;
    ipv4_key.lport = sk->__sk_common.skc_num;
    dport = sk->__sk_common.skc_dport;
    ipv4_key.dport = ntohs(dport);
    ipv4_send_bytes.increment(ipv4_key);

    return 0;
}
"""

# load BPF program
b = BPF(text=bpf_text)
b.attach_kprobe(event="tcp_write_err", fn_name="trace_tcp_write_err")
#b.attach_kprobe(event="sk_wait_data", fn_name="trace_tcp_write_err")

TCPSessionKey = namedtuple('TCPSession', ['laddr', 'lport', 'daddr', 'dport'])
def get_ipv4_session_key(k):
    return TCPSessionKey(laddr=inet_ntop(AF_INET, pack("I", k.saddr)),
                         lport=k.lport,
                         daddr=inet_ntop(AF_INET, pack("I", k.daddr)),
                         dport=k.dport)

label = "msecs"
exiting = 0
ipv4_send_bytes = b["ipv4_send_bytes"]

while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    for k, v in ipv4_send_bytes.items():
        key = get_ipv4_session_key(k)
        print(time.ctime(),key)
    ipv4_send_bytes.clear()

    if exiting:
        exit()
