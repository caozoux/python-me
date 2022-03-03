import os
import re
import json
import subprocess
import random
#from __future__ import print_function
from bcc import BPF
from time import sleep, strftime
import argparse
import signal
from subprocess import call
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()

def KvmBccRun(case):
    print("PerfStatRun")
    pass

bcclist={
"kvm":KvmBccRun,
}


kvmbpf_text = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
    return 0;
}
""")

print(kvmbpf_text)
