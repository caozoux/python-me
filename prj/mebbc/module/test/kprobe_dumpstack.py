
#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from time import sleep

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

struct key_t {
    int  w_k_stack_id;
    char waker[TASK_COMM_LEN];
    char target[TASK_COMM_LEN];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
BPF_STACK_TRACE(stack_traces, STACK_STORAGE_SIZE);
BPF_STACK_TRACE(stack_traces, STACK_STORAGE_SIZE);

int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
    struct key_t key = {};

    key.w_k_stack_id = stack_traces.get_stackid(ctx, BPF_F_REUSE_STACKID);
    return 0;
}
""")

# header
print("Tracing... Hit Ctrl-C to end.")

# trace until Ctrl-C
try:
    sleep(99999999)
except KeyboardInterrupt:
    print()
