from __future__ import print_function
from time import sleep, strftime
from bcc import BPF

g_sleep=1

def install_trace_evnet(bpf, event, func, hashd, handle_callback, sec=g_sleep):
    """install trace event function
    :event: event name such as "sched:sched_switch"
    :func:  trace event bpf function name
    :hashd:  hash data for record trace event
    :handle_callback:  handle the hash data of trace event
    """
    bpf.attach_tracepoint(tp=event, fn_name=func)
    counts = bpf.get_table(hashd)
    exiting = 0
    while 1:
        try:
            sleep(sec)
        except KeyboardInterrupt:
            exiting = 1
        handle_callback(counts)
        if exiting == 1:
            print("Detaching...")
            exit()
