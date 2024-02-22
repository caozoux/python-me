#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF
from time import sleep, strftime

#!/usr/bin/python3
# @lint-avoid-python-3-compatibility-imports

from __future__ import print_function
from bpfcc import BPF, USDT
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
} lock_key;

typedef struct {
    u64 ip;
    u64 start_ts;
} func_cache_t;

typedef struct {
    u64 ts;
    u64 lock;
} lock_data;

BPF_HASH(ipaddr, u32);
BPF_HISTOGRAM(dist);
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
    if (lock.lock != 0xffffffffa3c4f6e0)
      return 0;

    //u64 ip = PT_REGS_IP(ctx);
    //ipaddr.update(&pid, &ip);
    //start.update(&pid, &ts);
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

    // calculate delta time
    lock = start.lookup(&pid);
    if (lock == 0) {
        return 0;   // missed start
    }

    delta = bpf_ktime_get_ns() - lock->ts;
    start.delete(&pid);

    u32 lat = 0;
    u32 cnt = 1;
    avg.atomic_increment(lat, delta);
    avg.atomic_increment(cnt);

    delta = delta/1000000;
    if (delta > 100) {
        lock_key key = {};
        key.lock_addr = lock->lock;
        key.pid = pid;
        key.latency = delta;
        bpf_get_current_comm(&key.comm, 16);
        //dist.atomic_increment(bpf_log2l(delta));
        lock_hash.atomic_increment(key);
     }

    return 0;
}
"""

examples = """examples:
"""
parser = argparse.ArgumentParser(
    description="Trace slow kernel or user function calls.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-m", "--min-ms", type=float, dest="min_ms",
    help="minimum duration to trace (ms)")
args = parser.parse_args()

b = BPF(text=bpf_text)
#b.attach_kprobe(event_re="down_read", fn_name="trace_func_entry")
#b.attach_kretprobe(event_re="down_read", fn_name="trace_func_return")
#b.attach_kprobe(event_re="percpu_down_write", fn_name="trace_func_entry")
#b.attach_kretprobe(event_re="percpu_down_write", fn_name="trace_func_return")
b.attach_kprobe(event_re="mutex_lock", fn_name="trace_func_entry")
b.attach_kretprobe(event_re="mutex_lock", fn_name="trace_func_return")

exiting = 0
dist = b.get_table("dist")
lock_key = b.get_table("lock_hash")
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    for key in lock_key.keys():
        print("comm:%s addr:%x latency:%ld"%(key.comm, key.lock_addr, key.latency))

    lock_key.clear()
    dist.print_log2_hist("nsecs")
    dist.clear()

    if exiting:
        print("Detaching...")
        exit()
