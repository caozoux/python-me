from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
from mebccapi import tracevent
import argparse

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <include/event/sched.h>

typedef struct {
    char comm[16];
} sched_switch_task;

BPF_HASH(sched_switch_hash, sched_switch_task );

int trace_sched_switch(sched_switch_data *ctx)
{
    u64 ts = bpf_ktime_get_ns();
    sched_switch_task data={};
    bpf_probe_read_kernel(&data.comm, sizeof(data.comm), ctx->prev_comm);
    sched_switch_hash.update(&data, &ts);
    return 0;
}
"""

commDict={}
# load BPF program
b = BPF(text=bpf_text)

sched_trace_event_dict = {
    "sched:sched_switch":"",
}

def callback_sched(counts):
    exiting = 0
    print("==================================================")
    for k, v in counts.items():
        if not k.comm in commDict:
            commDict[k.comm] = 0
        else:
            commDict[k.comm] += 1 
        print(k.comm, commDict[k.comm])

tracevent.install_trace_evnet(b, "sched:sched_switch", "trace_sched_switch", "sched_switch_hash", callback_sched )

