#!/usr/bin/python3

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <linux/mm.h>

struct data_t {
    u64 count;
    u64 total_ns;
};

BPF_HASH(start, u64, u64);
BPF_HASH(data, u32, struct data_t);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 t = bpf_ktime_get_ns();

    if (pid_tgid >> 32 != FILTER_PID)
        return 0;

    start.update(&pid_tgid, &t);

    return 0;
}

TRACEPOINT_PROBE(raw_syscalls, sys_exit)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 t = bpf_ktime_get_ns();
    u32 key = args->id;

    if (pid_tgid >> 32 != FILTER_PID)
        return 0;

    struct data_t *val, zero = {};
    u64 *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    val = data.lookup_or_try_init(&key, &zero);
    if (val) {
        val->count++;
        val->total_ns += bpf_ktime_get_ns() - *start_ns;
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

parser.add_argument("-i", "--interval", type=int, dest="interval",
    help="summary interval, in seconds")
parser.add_argument("-p", "--pid", type=int, dest="pid",
    help="specify pid")

args = parser.parse_args()
if args.pid:
    bpf_text = bpf_text.replace("FILTER_PID", "%d"%args.pid)
else:
    bpf_text = bpf_text.replace("FILTER_PID", "0")

b = BPF(text=bpf_text)

data_key = b.get_table("data")
interval = 1
exiting = 0

agg_colname = "PID    COMM" if args.pid else "SYSCALL"
time_colname = "TIME (ms)"

def comm_for_pid(pid):
    try:
        return open("/proc/%d/comm" % pid, "rb").read().strip()
    except Exception:
        return b"[unknown]"

def agg_colval(key):
    return syscall_name(key.value)

def print_latency_stats():
    data = b["data"]
    print("[%s]" % strftime("%H:%M:%S"))
    print("%-22s %8s %16s" % (agg_colname, "COUNT", time_colname))
    for k, v in sorted(data.items(),
                       key=lambda kv: -kv[1].total_ns):
        if k.value == 0xFFFFFFFF:
            continue    # happens occasionally, we don't need it
        printb((b"%-22s %8d " + (b"%16.6f")) %
               (agg_colval(k), v.count,
                v.total_ns / (1e6)))
    print("")
    data.clear()

if args.interval:
    interval = args.interval

print("start trace..\n")
while 1:
    try:
        sleep(interval)
    except KeyboardInterrupt:
        exiting = 1
    print_latency_stats()
    data_key.clear()
    if exiting:
        exit(1)



