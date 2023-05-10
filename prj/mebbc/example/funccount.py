#!/usr/libexec/platform-python

from __future__ import print_function
from bcc import BPF
from time import sleep

# load BPF program
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
    return 0;
}
""")

# header
print("Tracing... Hit Ctrl-C to end.")


functions = BPF.get_kprobe_functions("blk_account_io_done")
print("functions:%v \n", functions);
#text += self._add_function(template, function)
#new_func = b"trace_count_%d" % self.matched
#text = template.replace(b"PROBE_FUNCTION", new_func)
#text = text.replace(b"LOCATION", b"%d" % self.matched)
#self.trace_functions[self.matched] = probe_name
#self.matched += 1

# trace until Ctrl-C
#try:
#    sleep(99999999)
#except KeyboardInterrupt:
    #print()
