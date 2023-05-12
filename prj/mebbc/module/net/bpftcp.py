from __future__ import print_function
from bcc import ArgString, BPF, USDT
from bcc import BPF
from bpfbase import KprobeBase

class bfptcp_sendmsg(KprobeBase):
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
        super(bpftcp_sendmsg, self).__init__()

    def attach(self, bpf):
        bpf.attach_kprobe(
                event=self.funcname,
                fn_name="bpf_tcp_connect")

    def report(self, bpf):
        sk=bpf["tcpsendmsg_sock"];
        for k, v in sorted(sk.items(),key=lambda counts: counts[1].value, reverse=True):
            print(k.value,v.value)

class bpftcp_connect(KprobeBase):
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
        super(bpftcp_connect, self).__init__()

    def report(self, bpf):
        sk=bpf["psock"];
        for k, v in sorted(sk.items(),key=lambda counts: counts[1].value, reverse=True):
            print(k.value,v.value)
