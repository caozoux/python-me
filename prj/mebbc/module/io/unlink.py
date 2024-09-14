from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse
import os

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
#include <linux/list.h>


typedef struct disk_key {
    char disk[DISK_NAME_LEN];
    u64 slot;
} disk_key_t;

struct data_t {
    u32 pid;
    char fcomm[TASK_COMM_LEN];
};

typedef struct disk_bio {
    u64 bi_vcnt;
} disk_bio_t;

BPF_PERF_OUTPUT(events);

static int local_strcmp(const char *cs, const char *ct)
{
    int len = 0;
    unsigned char c1, c2;

    while (len++ < 32) {
        c1 = *cs++;
        c2 = *ct++;
        if (c1 != c2)
            return c1 < c2 ? -1 : 1;
        if (!c1)
            break;
    }
    return 0;
}

// output
int trace_vfs_unlink(struct pt_regs *ctx, struct inode *dir, struct dentry *dentry, struct inode **delegated_inode)
{
    struct data_t data = {};
    char filter_devname[] = "11";
    char devname[32];

    if (!dentry)
        return 0;

    bpf_probe_read_kernel_str(devname, sizeof(devname), dentry->d_name.name);
    if (!local_strcmp(filter_devname, devname)) {
        u32 pid = bpf_get_current_pid_tgid() >> 32;
        data.pid = pid;
        bpf_get_current_comm(&data.fcomm, sizeof(data.fcomm));
        //bpf_trace_printk("%s", dentry->d_iname);
        events.perf_submit(ctx, &data, sizeof(data));
    }

    return 0;
}
"""
# process event
def print_event(cpu, data, size):
    event = b["events"].event(data)

    print(("%s Triggered by PID %d  %s") % \
           (strftime("%H:%M:%S"), event.pid, \
        event.fcomm.decode('utf-8', 'replace')))
    if os.path.exists("/proc/"+str(event.pid)):
        try:
            cmdline= open("/proc/"+str(event.pid)+"/cmdline", 'r').read()
            print(cmdline)
        except KeyboardInterrupt:
            exiting = 1


# load BPF program
b = BPF(text=bpf_text)
b.attach_kprobe(event="vfs_unlink", fn_name="trace_vfs_unlink")
b["events"].open_perf_buffer(print_event)

label = "msecs"
exiting = 0

while (1):
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exiting = 1


    if exiting:
        exit()
