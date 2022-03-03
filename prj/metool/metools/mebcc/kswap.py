from bcc import BPF
from time import sleep, strftime
import argparse
import signal
from subprocess import call
from optparse import OptionParser
bpf_text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct trace_mm_vmscan_kswapd_wake_data {
    u64 __unused__;
    unsigned int nid;
    unsigned int zid;
    unsigned int order;
};

struct hash_key {
    u64 ts;
    u64 pid;
    struct trace_mm_vmscan_kswapd_wake_data data;
};

BPF_HASH(py_hash, struct hash_key);

int trace_mm_vmscan_kswapd_wake(struct trace_mm_vmscan_kswapd_wake_data_*data)
{
    u64 ts = bpf_ktime_get_ns();
    u64 pid = bpf_get_current_pid_tgid();
    struct hash_key key= {};
    key.ts =ts;
    key.pid =pid;

    py_hash.increment(key);

}
"""

b = BPF(text=bpf_text)
b.attach_tracepoint(tp="vmscan:mm_vmscan_kswapd_wake", fn_name="trace_mm_vmscan_kswapd_wake")
counts = b.get_table("py_hash")

exiting = 0
while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    print("==================================================")
    for k, v in counts.items():
        print("%-40s%-10d"%(kvm_type[k.ts]))

    if exiting == 1:
        print("Detaching...")
        exit()

