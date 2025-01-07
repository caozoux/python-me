#!/usr/bin/python3

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <linux/mm.h>

typedef struct {
    u64 pid;
    char comm[16];
    u64 ts;
} key_data;

BPF_HASH(data_hash, key_data);

int kprobe_func(struct pt_regs *ctx) {
    key_data key = {};
    u16 sum = ctx->ax;

    if (sum == 0) {
        key.pid = bpf_get_current_pid_tgid();
        key.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&key.comm, 16);
        data_hash.increment(key);
    }


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
b.attach_kretkprobe(event="__skb_checksum_complete", fn_name="kprobe_func")

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

