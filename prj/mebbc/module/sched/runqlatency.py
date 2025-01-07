#! /usr/bin/python3
from __future__ import print_function
from bcc import BPF, PerfType, PerfSWConfig
import argparse
from time import strftime,sleep

# arguments
examples = """examples:
    ./runqslower         # trace run queue latency higher than 10000 us (default)
    ./runqslower 1000    # trace run queue latency higher than 1000 us
    ./runqslower -p 123  # trace pid 123
    ./runqslower -t 123  # trace tid 123 (use for threads only)
"""
parser = argparse.ArgumentParser(
    description="Trace high run queue latency",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("min_us", nargs="?", default='10000',
    help="minimum run queue latency to trace, in us (default 10000)")
parser.add_argument("--ebpf", action="store_true",
    help=argparse.SUPPRESS)

thread_group = parser.add_mutually_exclusive_group()
thread_group.add_argument("-p", "--pid", metavar="PID", dest="pid",
    help="trace this PID only", type=int)
thread_group.add_argument("-t", "--tid", metavar="TID", dest="tid",
    help="trace this TID only", type=int)
args = parser.parse_args()

min_us = int(args.min_us)
debug = 0

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/nsproxy.h>
#include <linux/pid_namespace.h>

BPF_HASH(start, u32);
BPF_HISTOGRAM(dist);

struct rq;

struct data_t {
    u32 pid;
    char task[TASK_COMM_LEN];
    u64 delta_us;
};

BPF_PERF_OUTPUT(events);

// record enqueue timestamp
static int trace_enqueue(u32 tgid, u32 pid)
{
    if (FILTER_PID || FILTER_TGID || pid == 0)
        return 0;
    u64 ts = bpf_ktime_get_ns();
    start.update(&pid, &ts);
    return 0;
}
"""

bpf_text_raw_tp = """
RAW_TRACEPOINT_PROBE(sched_wakeup)
{
    // TP_PROTO(struct task_struct *p)
    struct task_struct *p = (struct task_struct *)ctx->args[0];
    if (p->qos_level == SCHED_QOS_LC)
      return trace_enqueue(p->tgid, p->pid);
    return 0;
}

RAW_TRACEPOINT_PROBE(sched_wakeup_new)
{
    // TP_PROTO(struct task_struct *p)
    struct task_struct *p = (struct task_struct *)ctx->args[0];
    u32 tgid, pid;

    if (p->qos_level == SCHED_QOS_LC) {
      bpf_probe_read_kernel(&tgid, sizeof(tgid), &p->tgid);
      bpf_probe_read_kernel(&pid, sizeof(pid), &p->pid);
      return trace_enqueue(tgid, pid);
    }
    return 0;
}

RAW_TRACEPOINT_PROBE(sched_switch)
{
    // TP_PROTO(bool preempt, struct task_struct *prev, struct task_struct *next)
    struct task_struct *prev = (struct task_struct *)ctx->args[1];
    struct task_struct *next= (struct task_struct *)ctx->args[2];
    u32 tgid, pid;
    long state;

    // ivcsw: treat like an enqueue event and store timestamp
    bpf_probe_read_kernel(&state, sizeof(long), (const void *)&prev->state);
    if (state == TASK_RUNNING) {
        bpf_probe_read_kernel(&tgid, sizeof(prev->tgid), &prev->tgid);
        bpf_probe_read_kernel(&pid, sizeof(prev->pid), &prev->pid);
        u64 ts = bpf_ktime_get_ns();
        if (pid != 0) {
            if (!(FILTER_PID) && !(FILTER_TGID)) {
                if (prev->qos_level == SCHED_QOS_LC)
                  start.update(&pid, &ts);
            }
        }
    }

    bpf_probe_read_kernel(&pid, sizeof(next->pid), &next->pid);

    u64 *tsp, delta_us;

    // fetch timestamp and calculate delta
    tsp = start.lookup(&pid);
    if (tsp == 0) {
        return 0;   // missed enqueue
    }
    delta_us = (bpf_ktime_get_ns() - *tsp) / 1000;

    dist.increment(bpf_log2l(delta));

    start.delete(&pid);
    return 0;
}
"""

is_support_raw_tp = BPF.support_raw_tracepoint()
if is_support_raw_tp:
    bpf_text += bpf_text_raw_tp

if args.tid:
    bpf_text = bpf_text.replace('FILTER_PID', 'pid != %s' % args.tid)
else:
    bpf_text = bpf_text.replace('FILTER_PID', '0')

if args.pid:
    bpf_text = bpf_text.replace('FILTER_TGID', 'tgid != %s' % args.pid)
else:
    bpf_text = bpf_text.replace('FILTER_TGID', '0')

if debug or args.ebpf:
    print(bpf_text)
    if args.ebpf:
        exit()

# process event
def print_event(cpu, data, size):
    event = b["events"].event(data)
    print("%-8s %-16s %-6s %14s" % (strftime("%H:%M:%S"), event.task, event.pid, event.delta_us))

# load BPF program
b = BPF(text=bpf_text)

print("Tracing run queue latency higher than %d us" % min_us)
print("%-8s %-16s %-6s %14s" % ("TIME", "COMM", "TID", "LAT(us)"))

# read events
exiting = 0

while 1:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        exit()

    dist.print_log2_hist("usec")
    dist.clear()

    if exiting == 1:
        exit(0)
