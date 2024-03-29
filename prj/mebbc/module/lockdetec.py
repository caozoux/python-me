#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF

# usr/bin/python3
#from __future__ import print_function
#from bpfcc import BPF, USDT

from time import sleep, strftime
import argparse
import signal

bpf_text = """
#include <uapi/linux/ptrace.h>

typedef struct {
    u64 lock_addr;
    u64 pid;
    char comm[16];
    u64 latency;
    u64 sched_latency;
} lock_key;

typedef struct {
    u64 ip;
    u64 start_ts;
} func_cache_t;

typedef struct {
    u64 ts;
    u64 lock;
    u64 wake_ts;
} lock_data;

BPF_HASH(ipaddr, u32);
BPF_HASH(start, u32, lock_data);
BPF_ARRAY(avg, u64, 2);
BPF_HASH(lock_hash, lock_key);

int trace_func_entry(struct pt_regs *ctx)
{
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid;
    u32 tgid = pid_tgid >> 32;
    u64 ts = bpf_ktime_get_ns();
    lock_data lock = {};

    lock.lock = ctx->di;
    lock.ts = ts;
    lock.wake_ts = 0;

    if (LOCK)
      return 0;

    start.update(&pid, &lock);

    return 0;
}

int trace_func_return(struct pt_regs *ctx)
{
    u64 *tsp, delta;
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid;
    u32 tgid = pid_tgid >> 32;
    lock_data *lock;
    u64 ts;

    // calculate delta time
    lock = start.lookup(&pid);
    if (lock == 0) {
        return 0;   // missed start
    }
    
    ts = bpf_ktime_get_ns();
    delta = ts - lock->ts;
    start.delete(&pid);

    if (FILTER) {
        lock_key key = {};
        key.lock_addr = lock->lock;
        key.pid = pid;
        key.latency = delta;
        if (SCHED_TRACE) {
            key.sched_latency = ts - lock->wake_ts;
        }
        bpf_get_current_comm(&key.comm, 16);
        lock_hash.atomic_increment(key);
     }

    return 0;
}

#if ENABLE_SCHED
TRACEPOINT_PROBE(sched, sched_wakeup_new)
{
    u32 pid;
    lock_data *lock;

    pid = args->pid;

    lock = start.lookup(&pid);
    if (lock == 0)
        return 0;   // missed start

    lock->wake_ts = bpf_ktime_get_ns();
}

TRACEPOINT_PROBE(sched, sched_waking)
{
    u32 pid;
    lock_data *lock;

    pid = args->pid;

    lock = start.lookup(&pid);
    if (lock == 0)
        return 0;   // missed start

    lock->wake_ts = bpf_ktime_get_ns();
}

TRACEPOINT_PROBE(sched, sched_wakeup)
{
    u32 pid;
    lock_data *lock;

    pid = args->pid;

    lock = start.lookup(&pid);

    if (lock == 0)
        return 0;   // missed start

    lock->wake_ts = bpf_ktime_get_ns();
}
#endif

"""

examples = """examples:
    -m  throstle msecondecs
    -t  mutex_lock/rwsem/percpu_rwsem
"""

parser = argparse.ArgumentParser(
    description="Trace slow kernel or user function calls.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-m", "--min-ms", type=float, dest="min_ms",
    help="minimum duration to trace (ms)")
parser.add_argument("-l", "--lock", type=str, dest="lock",
    help="specify the lock addr")
parser.add_argument("-t", "--type-ms", type=str, dest="type",
    help="mutex/rwsem/per_rwsemu")

args = parser.parse_args()

if args.min_ms:
    bpf_text = bpf_text.replace('FILTER', 'delta >= %ld' % (args.min_ms * 1000000))
else:
    bpf_text = bpf_text.replace('FILTER', '1')

if args.lock:
    bpf_text = bpf_text.replace('LOCK', ('lock.lock != %s')%args.lock)
    bpf_text = bpf_text.replace('SCHED_TRACE', '1')
    bpf_text = bpf_text.replace('ENABLE_SCHED', '1')
else:
    bpf_text = bpf_text.replace('LOCK', '0')
    bpf_text = bpf_text.replace('SCHED_TRACE', '0')
    bpf_text = bpf_text.replace('ENABLE_SCHED', '0')

b = BPF(text=bpf_text)
if args.type == "rwsem":
    b.attach_kprobe(event="down_read", fn_name="trace_func_entry")
    b.attach_kretprobe(event="down_read", fn_name="trace_func_return")
elif args.type == "per_rwsem":
    b.attach_kprobe(event="percpu_down_read", fn_name="trace_func_entry")
    b.attach_kretprobe(event="percpu_down_read", fn_name="trace_func_return")
elif args.type == "mutex":
    b.attach_kprobe(event="mutex_lock", fn_name="trace_func_entry")
    b.attach_kretprobe(event="mutex_lock", fn_name="trace_func_return")
else:
    print("not specify the lock type");
    exit(0)

exiting = 0
lock_key = b.get_table("lock_hash")

while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    for key in lock_key.keys():
        print("comm:%s addr:%x latency:%ld"%(key.comm, key.lock_addr, key.latency))

    lock_key.clear()

    if exiting:
        print("Detaching...")
        exit()
