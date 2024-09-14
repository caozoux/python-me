#!/usr/libexec/platform-python


from __future__ import print_function
from bcc import BPF
from time import sleep, strftime

from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <linux/mm.h>
#include <linux/blkdev.h>
#include <linux/blk-mq.h>

typedef struct {
    u64 pid;
    char comm[16];
    u64 ts;
} key_data;

BPF_HASH(req_hash, u64);
BPF_HISTOGRAM(dist, u64);

RAW_TRACEPOINT_PROBE(block_rq_issue)
{
    struct request *rq = (struct request *)ctx->args[1]; ;
    u64 *tsp;
    u64 delta;

    tsp = req_hash.lookup((u64*)&rq);
    if (tsp == 0) {
        return 0;   // missed enqueue
    }

    delta = bpf_ktime_get_ns() - *tsp;
    req_hash.delete((u64*)&rq);

    dist.increment(bpf_log2l(delta));

    return 0;
}

RAW_TRACEPOINT_PROBE(block_rq_insert)
{
    struct request *rq = (struct request *)ctx->args[1]; ;
    u64 ts = bpf_ktime_get_ns();
    int major, first_minor;

    major = rq->rq_disk->major;
    first_minor = rq->rq_disk->first_minor;

    if (major == 65 && first_minor == 112) {
        req_hash.update((u64*)&rq, &ts);
    }

    return 0;
}

int trace_dispatch_entry(struct pt_regs *ctx)
{
    struct blk_mq_hw_ctx *hctx = ctx->di;
    struct request_queue *q = hctx->queue;
    if (q == 0xffff9c2d58d6d778)
        bpf_trace_printk("zz %lx\\n", q);
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

parser.add_argument("-", "--interval", type=int, dest="interval",
    help="summary interval, in seconds")

args = parser.parse_args()

b = BPF(text=bpf_text)
b.attach_kprobe(event="blk_mq_sched_dispatch_requests", fn_name="trace_dispatch_entry")

dist = b.get_table("dist")
interval = 1
exiting = 0

if args.interval:
    interval = args.interval

print("start trace..\n")
while 1:
    try:
        sleep(interval)
    except KeyboardInterrupt:
        exiting = 1

    dist.print_log2_hist("ns")

    dist.clear()
    if exiting:
        exit(1)

