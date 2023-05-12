#! /usr/bin/python3
from __future__ import print_function
from bcc import ArgString, BPF, USDT
from bcc import BPF
from time import sleep, strftime
import argparse
import signal
import bpftcp

matched = 0
kprobe_funs=[]
seconds=0
exiting=0

trace_count_text = b"""
int PROBE_FUNCTION(void *ctx) {
    FILTERPID
    FILTERCPU
    int loc = LOCATION;
    u64 *val = counts.lookup(&loc);
    if (!val) {
        return 0;   // Should never happen, # of locations is known
    }
    (*val)++;
    return 0;
}
"""
bpf_text = b"""#include <uapi/linux/ptrace.h>
"""

examples = """examples:
    ./funclatency do_sys_open       # time the do_sys_open() kernel function
    ./funclatency -i 2 -d 10 open   # output every 2 seconds, for duration 10s
    ./funclatency -mTi 5 vfs_read   # output every 5 seconds, with timestamps
    ./funclatency -p 181 vfs_read   # time process 181 only
    ./funclatency -F 'vfs_r*'       # show one histogram per matched function
"""
parser = argparse.ArgumentParser(
    description="muilt func monitor",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)

parser.add_argument("-i", "--interval", type=int, help="summary interval in seconds")
parser.add_argument("-d", "--duration", type=int,
    help="total duration of trace, in seconds")
parser.add_argument("-r", "--regexp", action="store_true",
    help="use regular expressions. Default is \"*\" wildcards only.")
parser.add_argument("-p", "--pid", type=int,
    help="trace this PID only")
parser.add_argument("-T", "--timestamp", action="store_true",
    help="include timestamp on output")
parser.add_argument("-c", "--cpu",
    help="trace this CPU only")

args = parser.parse_args()
if args.duration and not args.interval:
    args.interval = args.duration
if not args.interval:
    args.interval = 99999999

class KprobeBase(object):

    """Docstring for KprobeBase. """

    def __init__(self, funcname):
        """TODO: to be defined. """
        self.funcname=funcname

    def __init__(self ):
        """TODO: to be defined. """
        self.funcname=""

    def filter(self, cpu, pid):
        if pid:
            self.bpf_text = self.bpf_text.replace(b'FILTERPID',
                b"""u32 pid = bpf_get_current_pid_tgid() >> 32;
                   if (pid != %d) { return 0; }""" % args.pid)
        else:
            self.bpf_text = self.bpf_text.replace(b'FILTERPID', b'')

        if cpu:
            self.bpf_text = self.bpf_text.replace(b'FILTERCPU',
                b"""u32 cpu = bpf_get_smp_processor_id();
                   if (cpu != %d) { return 0; }""" % int(args.cpu))
        else:
            self.bpf_text = self.bpf_text.replace(b'FILTERCPU', b'')

    # attach kprobe event
    def attach(self,bpf):
        pass

    # load bpf txt to bpf
    def append(self):
        return self.bpf_text

    def update(self):
        pass

    def dump(self):
        print(self.bpf_text)

    def report(self, bpf):
        pass

class tcp_sendmsg(KprobeBase):
    def __init__(self):
        self.bpf_text= b"""
        #include <net/sock.h>
        BPF_HASH(tcpsendmsg_sock, struct sock *);
        int kprobe__tcp_sendmsg(struct pt_regs *ctx, struct sock *sk,
                 struct msghdr *msg, size_t size) 
        {
            //struct sock * sk= (struct sock *)ctx->di;
            FILTERPID
            FILTERCPU
            bpf_trace_printk("zz\\n");
            tcpsendmsg_sock.increment(sk, 1);
            //psock.update(&sk, &ts);
            return 0;
        }
        """
        super(tcp_sendmsg, self).__init__()

    def attach(self, bpf):
        bpf.attach_kprobe(
                event=self.funcname,
                fn_name="bpf_tcp_connect")

    def report(self, bpf):
        sk=bpf["tcpsendmsg_sock"];
        for k, v in sorted(sk.items(),key=lambda counts: counts[1].value, reverse=True):
            print(k.value,v.value)

class tcpconnect(KprobeBase):
    def __init__(self ):
        self.bpf_text= b"""
        #include <net/sock.h>
        BPF_HASH(psock, struct sock *);
        int kprobe__tcp_connect(struct pt_regs *ctx, struct sock *sk)
        {
            //struct sock * sk= (struct sock *)ctx->di;
            FILTERPID
            FILTERCPU
            psock.increment(sk, 1);
            return 0;
        }
        """
        super(tcpconnect, self).__init__()

    def report(self, bpf):
        sk=bpf["psock"];
        for k, v in sorted(sk.items(),key=lambda counts: counts[1].value, reverse=True):
            print(k.value,v.value)

mTcp=bpftcp.bpftcp_connect()
#mTcp=tcpconnect()
#mTcp.filter(args.cpu, args.pid)
#bpf_text += mTcp.append()

#mTcpMsg=tcp_sendmsg()
#mTcpMsg.filter(args.cpu, args.pid)
#bpf_text += mTcpMsg.append()

bpf = BPF(text=bpf_text, usdt_contexts=[])
#mTcp.attach(bpf)

if args.duration and not args.interval:
    args.interval = args.duration
if not args.interval:
    args.interval = 99999999

while True:
    try:
        sleep(int(args.interval))
        seconds += int(args.interval)
    except KeyboardInterrupt:
        exiting = 1

    #mTcp.report(bpf)
    #mTcpMsg.report(bpf)
    if exiting:
        print("Detaching...")
        exit()
