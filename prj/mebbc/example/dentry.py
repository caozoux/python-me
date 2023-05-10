#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
# Do not import unicode_literals until #623 is fixed
# from __future__ import unicode_literals
from __future__ import print_function

from bcc import BPF
from collections import defaultdict
from time import strftime

import argparse
import curses
import pwd
import re
import signal
from time import sleep

bpf_text = """
#include <linux/memcontrol.h>
#include <linux/mm.h>
#include <linux/fs.h>
#include <uapi/linux/ptrace.h>
#include <linux/genhd.h>

int h_major = 8;
int h_minors =2;
BPF_HASH(start, unsigned long);
//BPF_HASH(start, struct path*);
//BPF_HASH(start, structpt_regsdentry*);
int bpf_dentry_open(struct pt_regs *ctx)
{
    struct file *fd  = (struct file*)ctx->di;
    struct path *path = &fd->f_path;
    int flags = (int)ctx->si;
    struct dentry *dentry;
    struct inode *inode;
    unsigned long   i_ino;
    struct gendisk *disk;
    int major, minors;

    //if (flags == O_CREAT) {
    dentry = path->dentry;
    if (!dentry)
        goto out;

    if (!dentry->d_inode)
        goto out;

    inode = dentry->d_inode; 
    i_ino = inode->i_ino;

    start.increment(i_ino, 1);
    if (!dentry->d_sb ||  !dentry->d_sb->s_bdev)
        goto out;

    //start.increment(path, 1);
    disk = dentry->d_sb->s_bdev->bd_disk; 
    bpf_probe_read_kernel((void*)&major, sizeof(int),  &disk->major);
    bpf_probe_read_kernel((void*)&minors, sizeof(int), &disk->minors);
    if (major != h_major)
        goto out;
    if (minors != h_minors)
        goto out;

    //}

out:
    return 0;
}


"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="do_dentry_open", fn_name="bpf_dentry_open")
#counts = b.get_table("counts")
start = b["start"]
exiting = 0

while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        print("zz")
        for k, v in start.items():
            print(k.value)
        exit(0)
