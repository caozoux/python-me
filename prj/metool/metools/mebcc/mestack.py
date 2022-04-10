from bcc import BPF
from bcc.utils import printb
from time import sleep, strftime
import argparse
import signal
import errno
from subprocess import call
from optparse import OptionParser
from mebccapi import ArchX86Data

bpf_text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct key_t {
    int  w_k_stack_id;
    //char waker[TASK_COMM_LEN];
    //char target[TASK_COMM_LEN];
};

BPF_STACK_TRACE(stack_traces, 1024);
BPF_HASH(counts, struct key_t);
struct kvm_exit_key {
    int exit_reason;
};

int stacktrace(struct pt_regs *ctx, struct task_struct *p) {
    struct key_t key = {};
    //u64 delta ;

    //delta = bpf_ktime_get_ns();
    //delta = delta / 1000;
    key.w_k_stack_id = stack_traces.get_stackid(ctx, BPF_F_REUSE_STACKID);
    //counts.increment(key, delta);
    counts.increment(key);
    return 0;
}

"""

def GetFuncList(name):
    name=name.replace(" ","")
    name=name.split("+")
    return name

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-f", "--func", type="string", dest="func",
                  help="--f print the stacktrace of kernel function")

(options, args) = parser.parse_args()


if not options.func:
    exit(1)

funclist=GetFuncList(options.func)
b = BPF(text=bpf_text)

for func in funclist:
    b.attach_kprobe(event=func, fn_name="stacktrace")

#b.attach_kprobe(event="try_to_wake_up", fn_name="stacktrace")

exiting = 0
while (1):
    try:
        sleep(10)
    except KeyboardInterrupt:
        exiting = 1
        # as cleanup can take many seconds, trap Ctrl-C:
        #signal.signal(signal.SIGINT, signal_ignore)
    counts = b.get_table("counts")
    stack_traces = b.get_table("stack_traces")
    for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
        if k.w_k_stack_id == -errno.ENOMEM:
            missing_stacks += 1
            continue

        waker_kernel_stack = [] if k.w_k_stack_id < 1 else \
            reversed(list(stack_traces.walk(k.w_k_stack_id))[1:])
        # print default multi-line stack output
        #printb(b"2    %-16s %s" % (b"target:", k.target))
        for addr in waker_kernel_stack:
            printb(b"3    %-16x %s" % (addr, b.ksym(addr)))
        #printb(b"4    %-16s %s" % (b"waker:", k.waker))
        print("5        %d\n" % v.value)
    counts.clear()
    if exiting:
        exit()
