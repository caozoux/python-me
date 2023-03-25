#!/usr/bin/python
from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse


bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

typedef struct disk_key {
    char disk[DISK_NAME_LEN];
    u64 slot;
} disk_key_t;

typedef struct flag_key {
    u64 flags;
    u64 slot;
} flag_key_t;

BPF_HASH(start, struct request *);
STORAGE

// time block I/O
int trace_req_start(struct pt_regs *ctx, struct request *req)
{
    u64 ts = bpf_ktime_get_ns();
    start.update(&req, &ts);
    return 0;
}

// output
int trace_req_done(struct pt_regs *ctx, struct request *req)
{
    u64 *tsp, delta;

    // fetch timestamp and calculate delta
    tsp = start.lookup(&req);
    if (tsp == 0) {
        return 0;   // missed issue
    }
    delta = bpf_ktime_get_ns() - *tsp;
    FACTOR

    // store as histogram
    STORE

    start.delete(&req);
    return 0;
}
"""

bpf_text = bpf_text.replace('FACTOR', 'delta /= 1000;')
label = "usecs"
bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist);')
bpf_text = bpf_text.replace('STORE', 'dist.increment(bpf_log2l(delta));')
 
# load BPF program
b = BPF(text=bpf_text)

if BPF.get_kprobe_functions(b'blk_start_request'):
    b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")

b.attach_kprobe(event="blk_account_io_done",
    fn_name="trace_req_done")

print("Tracing block device I/O... Hit Ctrl-C to end.")
# see blk_fill_rwbs():
req_opf = {
    0: "Read",
    1: "Write",
    2: "Flush",
    3: "Discard",
    5: "SecureErase",
    6: "ZoneReset",
    7: "WriteSame",
    9: "WriteZeros"
}
REQ_OP_BITS = 8
REQ_OP_MASK = ((1 << REQ_OP_BITS) - 1)
REQ_SYNC = 1 << (REQ_OP_BITS + 3)
REQ_META = 1 << (REQ_OP_BITS + 4)
REQ_PRIO = 1 << (REQ_OP_BITS + 5)
REQ_NOMERGE = 1 << (REQ_OP_BITS + 6)
REQ_IDLE = 1 << (REQ_OP_BITS + 7)
REQ_FUA = 1 << (REQ_OP_BITS + 9)
REQ_RAHEAD = 1 << (REQ_OP_BITS + 11)
REQ_BACKGROUND = 1 << (REQ_OP_BITS + 12)
REQ_NOWAIT = 1 << (REQ_OP_BITS + 13)
def flags_print(flags):
    desc = ""
    # operation
    if flags & REQ_OP_MASK in req_opf:
        desc = req_opf[flags & REQ_OP_MASK]
    else:
        desc = "Unknown"
    # flags
    if flags & REQ_SYNC:
        desc = "Sync-" + desc
    if flags & REQ_META:
        desc = "Metadata-" + desc
    if flags & REQ_FUA:
        desc = "ForcedUnitAccess-" + desc
    if flags & REQ_PRIO:
        desc = "Priority-" + desc
    if flags & REQ_NOMERGE:
        desc = "NoMerge-" + desc
    if flags & REQ_IDLE:
        desc = "Idle-" + desc
    if flags & REQ_RAHEAD:
        desc = "ReadAhead-" + desc
    if flags & REQ_BACKGROUND:
        desc = "Background-" + desc
    if flags & REQ_NOWAIT:
        desc = "NoWait-" + desc
    return desc


countdown=99999999
exiting = 0
dist = b.get_table("dist")
print("mebcc start")
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1
    print()
    dist.print_log2_hist(label, "disk")
    dist.clear()
    countdown -= 1
    if exiting or countdown == 0:
        exit()
