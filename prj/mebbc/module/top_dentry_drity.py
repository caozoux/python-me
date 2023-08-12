#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
# Do not import unicode_literals until #623 is fixed
# from __future__ import unicode_literals
from __future__ import print_function

from bcc import BPF
from bcc.utils import printb
from collections import defaultdict
from time import strftime

import argparse
import curses
import pwd
import re
import signal
from time import sleep

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>
#include <linux/fs.h>
#include <linux/cgroup-defs.h>

int kprobe_dump_dentry(struct pt_regs *ctx)
{
    char *parent = (char *)ctx->di;
    char *child = (char *)ctx->si;
    char p_name[32];
    char c_name[32];

    bpf_probe_read_kernel(p_name, 32, parent);
    bpf_probe_read_kernel(c_name, 32, child);

     
}

"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="__put_task_struct", fn_name="kprobe_put_task_struct")
