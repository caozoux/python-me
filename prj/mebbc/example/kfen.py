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

KFUNC_PROBE(HOOK_FUNC, void *addr)
{
    trace_func_entry_handle((u64)addr);
    return 0;
}

KRETFUNC_PROBE(HOOK_FUNC, void *addr, int ret)
{

    trace_func_exit_handle();
    return 0;
}

int kprobe_func(struct pt_regs *ctx) {
    key_data key = {};

    key.pid = bpf_get_current_pid_tgid();
    key.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&key.comm, 16);
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

is_support_kfunc = BPF.support_kfunc()
if not is_support_kfunc:
    print("Err: kfunc not support")
    exit(1)

b = BPF(text=bpf_text)
b.attach_kprobe(event="down_read", fn_name="kprobe_func")

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

