#!/usr/libexec/platform-python
# @lint-avoid-python-3-compatibility-imports

from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse
import signal

# arguments
examples = """examples:
    ./funclatency 100               # monitor the lock latency more than 100 us
    ./funclatency -m 100            # monitor the lock latency more than 100 milliseconds
    ./funclatency -p 181 100        # monitor process 181 only
"""
parser = argparse.ArgumentParser(
    description="Time functions and print latency as a histogram",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-p", "--pid", type=int,
    help="trace this PID only")
parser.add_argument("-i", "--interval", type=int,
    help="summary interval, in seconds")
parser.add_argument("-d", "--duration", type=int,
    help="total duration of trace, in seconds")
parser.add_argument("-T", "--timestamp", action="store_true",
    help="include timestamp on output")
parser.add_argument("-v", "--verbose", action="store_true",
    help="print the BPF program (for debugging purposes)")
parser.add_argument("pattern",
    help="threshold time")
args = parser.parse_args()
if args.duration and not args.interval:
    args.interval = args.duration
if not args.interval:
    args.interval = 99999999

def bail(error):
    print("Error: " + error)
    exit(1)

pattern = args.pattern

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>

struct lock_report{
  int stackid;
  u64 laddr;
};

BPF_STACK_TRACE(stack_traces, 2048);
BPF_HASH(report_lock, struct lock_report);

int mutex_lock_return(struct pt_regs *ctx)
{
    struct lock_report l_report = { };
    l_report.stackid = stack_traces.get_stackid(ctx, 0);
    u64 ts = bpf_ktime_get_ns();

    l_report.laddr = ctx->di;
    report_lock.atomic_increment(l_report, ts);

    return 0;
}
"""

#bpf_text = bpf_text.replace('FILTER',
    #'if ( delta <= %d) { return 0; }' % int(pattern)*1000)

# code substitutions
label = "msecs"

# load BPF program
b = BPF(text=bpf_text)

# attach probes
b.attach_kprobe(event="down_read", fn_name="trace_mutex_lock_entry")
b.attach_kprobe(event="down_read", fn_name="trace_mutex_lock_exit")
b.attach_kprobe(event="mutex_lock", fn_name="trace_down_read")
matched = b.num_open_kprobes()

stack_traces = b.get_table("stack_traces")

# header
print("Tracing functions for \"lock\"... Hit Ctrl-C to end.")
exiting = 0

while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    print("\n%40s %10s %6s %10s %10s" % ("Caller", "Avg Spin", "Count", "Max spin", "Total spin"))
    report_lock = b.get_table("report_lock")
    stack_traces = b.get_table("stack_traces")
    for k, v in report_lock.items():
        print("%lx %ld"%(k.laddr, v.value))
        if k.stackid > 0 :
            kernel_stack = stack_traces.walk(k.stackid)
            for addr in kernel_stack:
                print("    %-16x %s" % (addr, b.ksym(addr)))

    #stack_traces.clear()
    report_lock.clear()

    if exiting:
        break;

