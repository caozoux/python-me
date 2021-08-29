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

BPF_HASH(start, struct request *);
BPF_HISTOGRAM(dist);

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

    delta /= 1000;
    dist.increment(bpf_log2l(delta));

    start.delete(&req);
    return 0;
}
"""

bpf_text = bpf_text.replace('STORAGE', 'BPF_HISTOGRAM(dist);')
bpf_text = bpf_text.replace('STORE',
    'dist.increment(bpf_log2l(delta));')
# load BPF program
b = BPF(text=bpf_text)
#b.attach_kprobe(event="blk_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_req_start")
b.attach_kprobe(event="blk_account_io_done",
    fn_name="trace_req_done")

label = "msecs"
exiting = 0

dist = b.get_table("dist")
while (1):
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    dist.print_log2_hist(label, "disk")
    dist.clear()

    if exiting:
        exit()
