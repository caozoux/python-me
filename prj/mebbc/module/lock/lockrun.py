#!/usr/bin/python3

from __future__ import print_function
from bpfcc import BPF
#from bpfcc import ArgString, BPF, USDT

from time import sleep, strftime
import argparse
import signal

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/pid_namespace.h>

typedef struct {
    u32 pid;
    char comm[16];
    u64 start_ts;
    u64 end_ts;
    int stack_id;
} lock_key;

BPF_HASH(start, u32, u64, 10240);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_PERF_OUTPUT(events);

static void trace_func_entry_handle(void *ctx)
{
    u32 pid;
    u64 ts;
    pid = bpf_get_current_pid_tgid();
    ts = bpf_ktime_get_ns();

    start.update(&pid, &ts);
    bpf_trace_printk("pid %d locked \\n", pid);
}

static void trace_func_exit_handle(void *ctx)
{
    u64 delta;
    u64 *entry_ts;
    u32 pid;
    u64 ts;

    pid = bpf_get_current_pid_tgid() & 0xFFFFFFFF;
    ts = bpf_ktime_get_ns();

    bpf_trace_printk("pid %d unlock \\n", pid);

    // calculate delta time
    entry_ts = start.lookup(&pid);
    if (entry_ts == 0)
        return;   // missed start

    delta = ts - *entry_ts;
    start.delete(&pid);
    if (FILTER) {
        lock_key key = {};
        key.pid = pid;
        key.start_ts = *entry_ts;
        key.end_ts = ts;
        //key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
        key.stack_id = 0;
        bpf_get_current_comm(&key.comm, 16);
        events.perf_submit(ctx, &key, sizeof(key));
    }
}


int trace_func_entry(struct pt_regs *ctx)
{
  u64 addr;  
  addr = (u64)ctx->di;
  if (MADDR)
    return 0;

  trace_func_entry_handle(ctx);
  return 0;
}

int trace_func_return(struct pt_regs *ctx)
{
  u64 addr;  
  addr = (u64)ctx->di;

  if (MADDR)
    return 0;

  trace_func_exit_handle(ctx);
  return 0;
}

#if ENABLE_FUNC

KFUNC_PROBE(HOOK_FUNC_UNLOCK, u64 addr)
{
  if (MADDR)
    return 0;

  trace_func_exit_handle(ctx);
  return 0;
}

KRETFUNC_PROBE(HOOK_FUNC_LOCKED, u64 addr, int ret)
{
  if (MADDR)
    return 0;

  trace_func_entry_handle(ctx);
  return 0;
}

KFUNC_PROBE(finish_task_switch, struct task_struct *prev)
{
  u32 pid;
  u64 *val, delta, ts;

  pid = bpf_get_current_pid_tgid();

  val = start.lookup(&pid);
  if (val == 0)
      return 0;

  ts = bpf_ktime_get_ns();
  delta = ts - *val;

  if (FILTER) {
    lock_key key = {};
    key.pid = pid;
    key.start_ts = *val;
    key.end_ts = ts;
    key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 1);
    //key.stack_id = 0;
    bpf_get_current_comm(&key.comm, 16);

    events.perf_submit(ctx, &key, sizeof(key));
  }

  return 0;

}
#endif

int finish_task_switch_trace(struct pt_regs *ctx, struct task_struct *prev)
{
    u32 pid;
    u64 *val, delta, ts;

    pid = bpf_get_current_pid_tgid();

    val = start.lookup(&pid);
    if (val == 0)
        return 0;

    ts = bpf_ktime_get_ns();
    delta = ts - *val;

    if (FILTER) {
      lock_key key = {};
      key.pid = pid;
      key.start_ts = *val;
      key.end_ts = ts;
      key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 1);
      //key.stack_id = 0;
      bpf_get_current_comm(&key.comm, 16);

      events.perf_submit(ctx, &key, sizeof(key));
    }
    return 0;
}

"""

examples = """examples:
    -m  throstle msecondecs
    -t  mutex_lock/rwsem/percpu_rwsem
"""

parser = argparse.ArgumentParser(
    description="Trace slow kernel or user function calls.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("-m", "--min-ms", type=float, dest="min_ms",
    help="minimum duration to trace (ms)")
parser.add_argument("-l", "--lock", type=str, dest="lock",
  help="specify the lock addr")
parser.add_argument("-f", "--function", type=str, dest="function",
    help="specify the hook function name")

args = parser.parse_args()

if args.min_ms:
    bpf_text = bpf_text.replace('FILTER', 'delta >= %ld' % (args.min_ms * 1000000))
else:
    bpf_text = bpf_text.replace('FILTER', '1')

if args.lock:
  print("enable sched latency");
  bpf_text = bpf_text.replace('MADDR', ('addr != %s')%args.lock)
else:
  print("disable sched latency");
  bpf_text = bpf_text.replace('MADDR', '0')

bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
bpf_text = bpf_text.replace('HOOK_FUNC_LOCKED', 'mutex_lock')
bpf_text = bpf_text.replace('HOOK_FUNC_UNLOCK', 'mutex_unlock')
b = BPF(text=bpf_text)

#b.attach_kprobe(event=args.function, fn_name="trace_func_entry")
#b.attach_kprobe(event='mutex_unlock', fn_name="trace_func_return")
#b.attach_kretprobe(event=args.function, fn_name="trace_func_return")
#b.attach_kprobe(event_re="^finish_task_switch$|^finish_task_switch\.isra\.\d$", fn_name="finish_task_switch_trace")

def print_event(cpu, data, size):
  key = b["events"].event(data)

  print("comm:%s pid:%d latency:%ld "%(key.comm, key.pid, key.end_ts - key.start_ts))
  if key.stack_id > 0:
    kernel_stack = stack_traces.walk(key.stack_id)
    for addr in kernel_stack:
      print(" %-16x %s" % (addr, b.ksym(addr)))

exiting = 0
stack_traces = b.get_table("stack_traces")
#b["start"].clear()
b["events"].open_perf_buffer(print_event, page_cnt=64)

print("start trace\n")

while (1):
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exiting = 1

    if exiting:
        print("Detaching...")
        exit()
