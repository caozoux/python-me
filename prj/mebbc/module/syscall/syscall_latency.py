#!/usr/bin/python3

from __future__ import print_function
from bcc import BPF
from bcc.utils import printb

from collections import defaultdict
import argparse
from time import sleep, strftime
from bcc.syscall import syscall_name, syscalls

bpf_text = """
#include <linux/mm.h>

struct data_t {
    u64 count;
    u64 total_ns;
};

typedef struct {
    u64 pid;
    u64 entry_ts;
    u64 switch_ts;
    int user_stack_id;
    int kernel_stack_id;
    u32 id;
} search_data;

typedef struct {
    u32 pid;
    u32 id;
    u64 delta;
    u64 sleep_delta;
    int user_stack_id;
    int kernel_stack_id;
} report_data_t;

BPF_PERF_OUTPUT(events);
BPF_HASH(start, u64, search_data);
BPF_HASH(data, u32, struct data_t);
BPF_STACK_TRACE(stack_traces, 2048);

TRACEPOINT_PROBE(raw_syscalls, sys_enter)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    search_data data;
    u32 id;

    if (pid_tgid >> 32 != FILTER_PID)
        return 0;
    id = args->id;
    if (EXTERN) {
       if (id == 202 || id == 35 || id == 232 || id == 230)
          return 0;
    }

    __builtin_memset(&data, 0, sizeof(search_data));
    data.entry_ts = bpf_ktime_get_ns();
    data.id = id;

    start.update(&pid_tgid, &data);

    return 0;
}

#ifdef  LATENCY_TOTAL
TRACEPOINT_PROBE(raw_syscalls, sys_exit)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 t = bpf_ktime_get_ns();
    u32 key = args->id;
    u64 delta;

    if (pid_tgid >> 32 != FILTER_PID)
        return 0;

    struct data_t *val, zero = {};
    search_data  *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    u64 ts = bpf_ktime_get_ns();
    delta = ts - start_ns->entry_ts;
    start.delete(&pid_tgid);

    if (delta < 10000000)
        return 0;

    bpf_trace_printk("%ld\\n", delta);

    val = data.lookup_or_try_init(&key, &zero);
    if (val) {
        val->count++;
        val->total_ns += bpf_ktime_get_ns() - start_ns->entry_ts;
    }

    return 0;
}
#endif

#ifdef LATENCY_THROTTLE
RAW_TRACEPOINT_PROBE(sched_switch)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();

    if (pid_tgid>>32 != FILTER_PID)
        return 0;

    search_data *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    start_ns->switch_ts = bpf_ktime_get_ns();
    start_ns->kernel_stack_id = stack_traces.get_stackid(ctx, (0 | BPF_F_FAST_STACK_CMP));
}

RAW_TRACEPOINT_PROBE(sys_exit)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u64 delta;
    u64 ts, sleep_ts;

    if (pid_tgid>>32 != FILTER_PID)
        return 0;

    search_data *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    ts = bpf_ktime_get_ns();
    delta = ts - start_ns->entry_ts;

    if (delta < THROTLE) {
        start.delete(&pid_tgid);
        return 0;
    }

    //bpf_trace_printk("%ld %ld\\n", delta, ts - start_ns->entry_ts);
#if 1
    report_data_t data = {};
    data.pid = pid_tgid;
    data.delta  = delta;
    data.id  = start_ns->id;

    if (start_ns->switch_ts)
        data.sleep_delta = ts - start_ns->switch_ts;
    else
        data.sleep_delta = 0;

    data.user_stack_id = stack_traces.get_stackid(ctx, BPF_F_USER_STACK);
    data.kernel_stack_id = start_ns->kernel_stack_id;
    events.perf_submit(ctx, &data, sizeof(data));
#endif
    start.delete(&pid_tgid);
}
#endif
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
parser.add_argument("-t", "--throttle", type=int, dest="throttle", default=0,
    help="throttle milliseconds")
parser.add_argument("-e", "--extern", action="store_true", dest="extern",
    help="specify pid")

args = parser.parse_args()
if args.pid:
    bpf_text = bpf_text.replace("FILTER_PID", "%d"%args.pid)
else:
    bpf_text = bpf_text.replace("FILTER_PID", "0")

if args.extern:
    bpf_text = bpf_text.replace("EXTERN", "1")
else:
    bpf_text = bpf_text.replace("EXTERN", "0")

if args.throttle:
    bpf_text = "#define LATENCY_THROTTLE\n" + bpf_text
    bpf_text = bpf_text.replace("THROTLE", "%d"%(args.throttle*1000000))
else:
    bpf_text = "#define LATENCY_TOTAL\n" + bpf_text
    bpf_text = bpf_text.replace("THROTLE", "0")

b = BPF(text=bpf_text)

data_key = b.get_table("data")
stack_traces = b.get_table("stack_traces")
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
        printb((b"%-22s %d %8d " + (b"%16.6f")) %
               (agg_colval(k), k.value, v.count,
                v.total_ns / (1e6)))
    print("")
    data.clear()

def print_event(cpu, data, size):
    event = b["events"].event(data)
    print("%-8s %-8s %-6s %-6s" % (strftime("%H:%M:%S"), syscall_name(event.id),
        event.delta/1000000, event.sleep_delta/1000000))
    if event.user_stack_id > 0:
      user_stack = stack_traces.walk(event.user_stack_id)
      for addr in user_stack:
          print("%s" % b.sym(addr, args.pid, show_offset=True))
    if event.kernel_stack_id > 0:
      kernel_stack = stack_traces.walk(event.kernel_stack_id)
      kernel_stack = list(kernel_stack)
      for addr in kernel_stack:
          sym_str = str(b.ksym(addr, show_offset=True))
          if "bpf" in sym_str:
              continue
          print(sym_str)
    print("\n")
    #if args.stack:
    # print_stack(event.stack_id)

if args.throttle:
    interval = args.interval
    b["events"].open_perf_buffer(print_event, page_cnt=64)

print("start trace..\n")
while 1:

    if args.throttle:
        try:
            b.perf_buffer_poll()
        except KeyboardInterrupt:
            exit()
    else:
        try:
            sleep(interval)
        except KeyboardInterrupt:
            exiting = 1

        print_latency_stats()
        data_key.clear()

        if exiting:
            exit(1)

