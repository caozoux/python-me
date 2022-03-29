from bcc import BPF
from time import sleep, strftime
import argparse
import signal
from subprocess import call
from optparse import OptionParser
from mebccapi import ArchX86Data

# load BPF program
kvmbpf_text="""

#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
struct kvm_exit_key {
    int exit_reason;
};

struct kvm_msr_key {
    unsigned int write;
    u64 data;
};

BPF_HASH(kvm_exit_hash, struct kvm_exit_key);

BPF_HASH(kvm_msr_hash, struct kvm_msr_key);

struct kvm_entrys_args {
    u64 pid;
    unsigned int  exit_reason;
    unsigned long guest_rip;
    u32  isa;
    u64 info1;
    u64 info2;
};

struct kvm_msr_args {
    u64 __unused__;
    unsigned int write;
    u32 ecx;
    u64 data;
    u8  except;
};

int trace_kvm_exit(struct kvm_entrys_args *ctx)
{
    struct kvm_exit_key key= {};
    unsigned int exit_reason= (unsigned int)ctx->exit_reason;
    bpf_trace_printk("%x %lx\\n", exit_reason, ctx->guest_rip);
    key.exit_reason=exit_reason;
    kvm_exit_hash.increment(key);
    //bpf_trace_printk("zz ");
}

int trace_kvm_msr(struct kvm_msr_args *ctx)
{
    struct kvm_msr_key key={};
    //unsigned int write= (unsigned int)ctx->write;
    //unsigned int ecx= (unsigned int)ctx->ecx;

    key.write = ctx->write;
    key.data = ctx->ecx;
    kvm_msr_hash.increment(key);
}
"""

kvm_trace_event_dict = {
"kvm:kvm_exit":"trace_kvm_exit",
"kvm:kvm_msr":"trace_kvm_msr",
}

def instance_kvm_exit():
    counts = b.get_table("kvm_exit_hash") 
# trace until Ctrl-C
    exiting = 0
    while 1:
        try:
            sleep(1)
        except KeyboardInterrupt:
            exiting = 1

        print("==================================================")
        for k, v in counts.items():
            print("%-40s%-10d"%(ArchX86Data.kvm_exit_type1[k.exit_reason], v.value))
            #print("%-30d%-10d"%(k.exit_reason, v.value))

        if exiting == 1:
            print("Detaching...")
            exit()

def instance_kvm_msr():
    b.attach_tracepoint(tp="kvm:kvm_msr", fn_name="trace_kvm_msr")
    #kvm_trace_event_dict['kvm:kvm_msr']()
    counts = b.get_table("kvm_msr_hash") 
    exiting = 0
    while 1:
        try:
            sleep(1)
        except KeyboardInterrupt:
            exiting = 1

        print("==================================================")
        for k, v in counts.items():
            if k.data in ArchX86Data.x86_msr_dict.keys():
                print("%-30s%-10x"%(ArchX86Data.x86_msr_dict[int(k.data)], v.value))
            else:
                print("%-30x%-10x"%(k.data, v.value))

        if exiting == 1:
            print("Detaching...")
            exit()

kvm_trace_event_dict = {
"kvm:kvm_exit":instance_kvm_exit,
"kvm:kvm_msr":instance_kvm_msr,
}

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run command")
(options, args) = parser.parse_args()


def RunCommand(key):
    if key in kvm_trace_event_dict.keys():
        kvm_trace_event_dict[key]()

def ListCommand(dictlist):
    for key in dictlist:
        print(("%s  %--20s")%("command:", key))

if options.list:
    ListCommand(kvm_trace_event_dict)
    exit(0)

if options.run:
    b = BPF(text=kvmbpf_text)
    RunCommand(options.run)

# header
#b.attach_tracepoint(tp="kvm:kvm_exit", fn_name="trace_kvm_exit")
#b.attach_tracepoint(tp="kvm:kvm_msr", fn_name="trace_kvm_msr")
#b.attach_tracepoint(tp="sched:sched_switch", fn_name="on_switch")
kvm_trace_event_dict['kvm:kvm_msr']()
