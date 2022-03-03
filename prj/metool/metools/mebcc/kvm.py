from bcc import BPF
from time import sleep, strftime
import argparse
import signal
from subprocess import call
from optparse import OptionParser

# load BPF program
kvmbpf_text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>
char test[]="hi";
struct key_t {
	int exit_reason;
};
BPF_HASH(kvm_record, struct key_t);
struct kvm_entrys_args {
    u64 __unused__;
    unsigned int data1;
    unsigned int data2;
    unsigned int data3;
};
struct kvm_msr_args {
    u64 __unused__;
    unsigned int write;
    unsigned int ecx;
    u64 exception;
};


int on_switch(struct kvm_entrys_args *ctx)
{
    struct key_t key= {};
    unsigned int exit_reason= (unsigned int)ctx->data1;
    //bpf_trace_printk("%d %d\\n", exit_reason, exit_reason);
    key.exit_reason=exit_reason;
    kvm_record.increment(key);
    //bpf_trace_printk("zz ");
}
int kvm_msr(struct kvm_msr_args *ctx)
{
    unsigned int write= (unsigned int)ctx->write;
    unsigned int ecx= (unsigned int)ctx->ecx;
    bpf_trace_printk("%d %x\\n", write, ecx);
    //key.exit_reason=exit_reason;
    //kvm_record.increment(key);
    //bpf_trace_printk("zz ");
}
"""

# header
b = BPF(text=kvmbpf_text)
#b.attach_tracepoint(tp="kvm:kvm_entry", fn_name="kvm_entry")
b.attach_tracepoint(tp="kvm:kvm_exit", fn_name="on_switch")
b.attach_tracepoint(tp="kvm:kvm_msr", fn_name="kvm_msr")
#b.attach_tracepoint(tp="sched:sched_switch", fn_name="on_switch")

kvm_type = [
"EXIT_REASON_EXCEPTION_NMI",
"EXIT_REASON_EXTERNAL_INTERRUPT",
"EXIT_REASON_TRIPLE_FAULT",
"EXIT_REASON_INIT_SIGNAL",
"EXIT_INVALID",
"EXIT_INVALID",
"EXIT_INVALID",
"EXIT_REASON_PENDING_INTERRUPT",
"EXIT_REASON_NMI_WINDOW",
"EXIT_REASON_TASK_SWITCH",
"EXIT_REASON_CPUID",
"EXIT_INVALID",
"EXIT_REASON_HLT",
"EXIT_REASON_INVD",
"EXIT_REASON_INVLPG",
"EXIT_REASON_RDPMC",
"EXIT_REASON_RDTSC",
"EXIT_INVALID",
"EXIT_REASON_VMCALL",
"EXIT_REASON_VMCLEAR",
"EXIT_REASON_VMLAUNCH",
"EXIT_REASON_VMPTRLD",
"EXIT_REASON_VMPTRST",
"EXIT_REASON_VMREAD",
"EXIT_REASON_VMRESUME",
"EXIT_REASON_VMWRITE",
"EXIT_REASON_VMOFF",
"EXIT_REASON_VMON",
"EXIT_REASON_CR_ACCESS",
"EXIT_REASON_DR_ACCESS",
"EXIT_REASON_IO_INSTRUCTION",
"EXIT_REASON_MSR_READ",
"EXIT_REASON_MSR_WRITE",
"EXIT_REASON_INVALID_STATE",
"EXIT_REASON_MSR_LOAD_FAIL",
"EXIT_INVALID",
"EXIT_REASON_MWAIT_INSTRUCTION",
"EXIT_REASON_MONITOR_TRAP_FLAG",
"EXIT_INVALID",
"EXIT_REASON_MONITOR_INSTRUCTION",
"EXIT_REASON_PAUSE_INSTRUCTION",
"EXIT_REASON_MCE_DURING_VMENTRY",
"EXIT_INVALID",
"EXIT_REASON_TPR_BELOW_THRESHOLD",
"EXIT_REASON_APIC_ACCESS",
"EXIT_REASON_EOI_INDUCED",
"EXIT_REASON_GDTR_IDTR",
"EXIT_REASON_LDTR_TR",
"EXIT_REASON_EPT_VIOLATION",
"EXIT_REASON_EPT_MISCONFIG",
"EXIT_REASON_INVEPT",
"EXIT_REASON_RDTSCP",
"EXIT_REASON_PREEMPTION_TIMER",
"EXIT_REASON_INVVPID",
"EXIT_REASON_WBINVD",
"EXIT_REASON_XSETBV",
"EXIT_REASON_APIC_WRITE",
"EXIT_REASON_RDRAND",
"EXIT_REASON_INVPCID",
"EXIT_REASON_VMFUNC",
"EXIT_REASON_ENCLS",
"EXIT_REASON_RDSEED",
"EXIT_REASON_PML_FULL",
"EXIT_REASON_XSAVES",
"EXIT_REASON_XRSTORS",
"EXIT_REASON_UMWAIT",
"EXIT_REASON_TPAUSE",
];
counts = b.get_table("kvm_record") 
# trace until Ctrl-C
exiting = 0
while 1:
    try:
        sleep(1)
    except KeyboardInterrupt:
        exiting = 1

    print("==================================================")
    for k, v in counts.items():
        print("%-40s%-10d"%(kvm_type[k.exit_reason], v.value))
        #print("%-30d%-10d"%(k.exit_reason, v.value))


    if exiting == 1:
        print("Detaching...")
        exit()

