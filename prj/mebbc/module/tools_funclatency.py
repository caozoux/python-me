#! /usr/bin/python3
from __future__ import print_function
from bcc import ArgString, BPF, USDT
from bcc import BPF
from time import sleep, strftime
import argparse
import signal

matched = 0
kprobe_funs=[]
seconds=0
exiting=0

bpf_text = """
#include <uapi/linux/ptrace.h>

typedef struct ip_pid {
    u64 ip;
    u64 pid;
} ip_pid_t;

typedef struct hist_key {
    ip_pid_t key;
    u64 slot;
} hist_key_t;

TYPEDEF

BPF_ARRAY(avg, u64, 2);
STORAGE
FUNCTION

int trace_func_entry(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid;
    u32 tgid = pid_tgid >> 32;
    u64 ts = bpf_ktime_get_ns();

    FILTER
    ENTRYSTORE

    return 0;
}

int trace_func_return(struct pt_regs *ctx)
{
    u64 *tsp, delta;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid;
    u32 tgid = pid_tgid >> 32;

    // calculate delta time
    CALCULATE

    u32 lat = 0;
    u32 cnt = 1;
    avg.atomic_increment(lat, delta);
    avg.atomic_increment(cnt);

    FACTOR

    // store as histogram
    STORE

    return 0;
}
"""

examples = """examples:
    ./funclatency do_sys_open       # time the do_sys_open() kernel function
    ./funclatency -i 2 -d 10 open   # output every 2 seconds, for duration 10s
    ./funclatency -mTi 5 vfs_read   # output every 5 seconds, with timestamps
    ./funclatency -p 181 vfs_read   # time process 181 only
    ./funclatency -F 'vfs_r*'       # show one histogram per matched function
"""
parser = argparse.ArgumentParser(
    description="muilt func monitor",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)

parser.add_argument("-i", "--interval", type=int, help="summary interval in seconds")
parser.add_argument("-d", "--duration", type=int,
    help="total duration of trace, in seconds")
parser.add_argument("pattern",type=ArgString,
    help="search expression for functions")
parser.add_argument("-r", "--regexp", action="store_true",
    help="use regular expressions. Default is \"*\" wildcards only.")
parser.add_argument("-p", "--pid", type=int,
    help="trace this PID only")
parser.add_argument("-T", "--timestamp", action="store_true",
    help="include timestamp on output")
parser.add_argument("-c", "--cpu",
    help="trace this CPU only")

args = parser.parse_args()
if args.duration and not args.interval:
    args.interval = args.duration
if not args.interval:
    args.interval = 99999999

if args.pid:
    trace_count_text = trace_count_text.replace(b'FILTERPID',
        b"""u32 pid = bpf_get_current_pid_tgid() >> 32;
           if (pid != %d) { return 0; }""" % args.pid)
else:
    trace_count_text = trace_count_text.replace(b'FILTERPID', b'')

if args.cpu:
    trace_count_text = trace_count_text.replace(b'FILTERCPU',
        b"""u32 cpu = bpf_get_smp_processor_id();
           if (cpu != %d) { return 0; }""" % int(args.cpu))
else:
    trace_count_text = trace_count_text.replace(b'FILTERCPU', b'')

parts = bytes(args.pattern).split(b':')

for funcname in parts:
    pattern=b'^' + funcname + b'$'
    functions = BPF.get_kprobe_functions(pattern)
    if not functions:
        continue

    new_func = b"trace_count_%d" % matched
    text = trace_count_text.replace(b"PROBE_FUNCTION", new_func)
    text = text.replace(b"LOCATION", b"%d" % matched)
    bpf_text += text
    matched += 1
    kprobe_funs.append(funcname)
    print("add func", funcname)

bpf_text = bpf_text.replace(b"NUMLOCATIONS",
                        b"%d" % len(parts))
bpf = BPF(text=bpf_text,
               usdt_contexts=[])

for i in range(len(kprobe_funs)):
    function=kprobe_funs[i]
    bpf.attach_kprobe(
            event=function,
            fn_name="trace_count_%d" % i)

if args.duration and not args.interval:
    args.interval = args.duration
if not args.interval:
    args.interval = 99999999

while True:
    try:
        sleep(int(args.interval))
        seconds += int(args.interval)
    except KeyboardInterrupt:
        exiting = 1

    print()
    counts = bpf["counts"]
    for k, v in sorted(counts.items(),
                       key=lambda counts: counts[1].value):
        if v.value == 0:
            continue
        print("%-36s %8d" %(kprobe_funs[k.value].decode('utf-8'), v.value))
    counts.clear()

    if exiting:
        print("Detaching...")
        exit()
