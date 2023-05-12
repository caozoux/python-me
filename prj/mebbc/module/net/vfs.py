from __future__ import print_function
from bcc import ArgString, BPF, USDT
from bcc import BPF
from bpfbase import KprobeBase

class bpfvfs_open(KprobeBase):
    def __init__(self):
        self.bpf_text= b"""
        #include <net/sock.h>
        BPF_HASH(tcpsendmsg_sock, struct sock *);
        int kprobe__vfs_open(struct pt_regs *ctx, struct sock *sk,
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
        super(bpfvfs_open, self).__init__()

