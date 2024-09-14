#!/usr/bin/python3

from __future__ import print_function
from bpfcc import BPF
#from bpfcc import ArgString, BPF, USDT

from time import sleep, strftime
from collections import defaultdict
import argparse
import signal
import time
import os

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/pid_namespace.h>

typedef struct {
  u64 lock_addr;
  u64 pid;
  char comm[16];
  u64 wait_latency;
  u64 run_latency;
  u64 sched_latency;
  int stack_id;
} lock_key;

typedef struct {
  u64 ip;
  u64 start_ts;
} func_cache_t;

typedef struct {
  u64 start_ts;
  u64 get_ts;
  u64 lock;
  u64 wake_ts;
} lock_data;

typedef struct {
  u32 pid;
  char comm[16];
  int stack_id;
} lock_stack_key;

struct depth_id {
  u64 id;
  u64 depth;
};

BPF_HASH(start, u32, lock_data, 51200);
//BPF_HASH(start, u32, lock_data, 10240);
BPF_ARRAY(avg, u64, 2);
BPF_HASH(lock_hash, lock_key);
BPF_STACK_TRACE(stack_traces, 1024);
BPF_HASH(stack_counts, lock_stack_key);
BPF_HASH(track,   u64, u64, 10240);
BPF_HASH(time_aq, u64, u64, 10240);
BPF_HASH(lock_depth, u64, u64, 10240);
BPF_HASH(time_held,  struct depth_id, u64, 10240);
BPF_HASH(stack,   struct depth_id, int, 10240);
//BPF_PERF_OUTPUT(events);

int trace_func_throttle(struct pt_regs *ctx)
{
  u32 pid = bpf_get_current_pid_tgid();
  lock_stack_key lock={};
  u64 addr = ctx->di;

  lock.pid = pid;
  bpf_get_current_comm(&lock.comm, 16);
  lock.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
  stack_counts.increment(lock);

  return 0;
}


int trace_func_unlock(struct pt_regs *ctx)
{
  u32 pid = bpf_get_current_pid_tgid();
  u64 delta;
  u64 d1,d2;
  u64 ts = bpf_ktime_get_ns();
  lock_data *lock;
  u64 addr = ctx->di;

  if (MADDR)
    return 0;

  lock = start.lookup(&pid);
  if (lock == 0) {
    return 0;   // missed start
  }

  if (lock->start_ts == 0 || lock->get_ts == 0) {
    start.delete(&pid);
    return 0;
  }

  d1 = ts - lock->get_ts;
  d2 = lock->get_ts - lock->start_ts;
  delta = d1 > d2 ? d1 : d2;

  if (FILTER) {
    lock_key key = {};
    u64 addr = ctx->di;
    key.lock_addr = addr;
    key.pid = pid;
    key.wait_latency = d2;
    key.run_latency = d1;
    if (lock->wake_ts)
      key.sched_latency = ts > lock->wake_ts ? ts - lock->wake_ts : 0;
    else
      key.sched_latency = 0;
    bpf_get_current_comm(&key.comm, 16);
    key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
    lock_hash.atomic_increment(key);
   }

  start.delete(&pid);
  return 0;
}

static void trace_func_entry_handle(void *ctx, u64 addr)
{
  u32 pid;
  u64 ts;
  pid = bpf_get_current_pid_tgid();
  ts = bpf_ktime_get_ns();

  lock_data lock = {};
  lock.lock = addr;
  lock.start_ts = ts;
  lock.get_ts = 0;
  lock.wake_ts = 0;

  ts = bpf_ktime_get_ns();

  start.update(&pid, &lock);
}

static void trace_func_return_handle(void *ctx)
{
  u64 delta;
  u32 pid;
  lock_data *lock;
  u64 ts;

  pid = bpf_get_current_pid_tgid();
  ts = bpf_ktime_get_ns();

  // calculate delta time
  lock = start.lookup(&pid);
  if (lock == 0) {
    return;   // missed start
  }

  if (NOT_SUPPORT_RUN) {
    delta = ts - lock->start_ts;
    if (FILTER) {
      lock_key key = {};
      key.lock_addr = lock->lock;
      key.pid = pid;
      key.pid = bpf_get_current_pid_tgid()>>32;
      key.wait_latency = delta;
      key.run_latency = 0;
      key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, true);
      //key.stack_id = 0;
      if (SCHED_TRACE) {
        key.sched_latency = ts > lock->wake_ts ? ts - lock->wake_ts : 0;
      }
      bpf_get_current_comm(&key.comm, 16);
  #if 1
      lock_hash.atomic_increment(key);
  #else
      //events.perf_submit(ctx, &key, sizeof(key));
  #endif
    }

    start.delete(&pid);

  } else {
    lock->get_ts = ts;
  }
}

#if ENABLE_FUNC
KFUNC_PROBE(HOOK_FUNC, u64 addr)
{
  if (MADDR)
    return 0;

  trace_func_entry_handle(ctx, (u64)addr);
  return 0;
}

KRETFUNC_PROBE(HOOK_FUNC, u64 addr, int ret)
{
  if (MADDR)
    return 0;

  trace_func_return_handle(ctx);
  return 0;
}
#else
int trace_func_entry(struct pt_regs *ctx)
{
  u64 addr = ctx->di;

  if (MADDR)
    return 0;

  trace_func_entry_handle(ctx, addr);
  return 0;
}

int trace_func_return(struct pt_regs *ctx)
{
  trace_func_return_handle(ctx);
  return 0;
}
#endif

int trace_func_mutex_entry(struct pt_regs *ctx)
{
  u64 id = bpf_get_current_pid_tgid();
  u64 addr = ctx->di;

  if (MADDR)
    return 0;

  u64 one = 1, zero = 0;

  track.update(&id, &one);

  u64 *depth = lock_depth.lookup(&id);

  if (!depth) {
    lock_depth.update(&id, &zero);

    depth = lock_depth.lookup(&id);
    /* something is wrong.. */
    if (!depth)
      return 0;
  }

  int stackid = stack_traces.get_stackid(ctx, 0);
  struct depth_id did = {
    .id = id,
    .depth = *depth,
  };

  stack.update(&did, &stackid);

  u64 ts = bpf_ktime_get_ns();
  time_aq.update(&id, &ts);

  *depth += 1;


  return 0;
}

int trace_func_mutex_return(struct pt_regs *ctx)
{
  u64 id = bpf_get_current_pid_tgid();

  u64 *one = track.lookup(&id);

  if (!one)
    return 0;

  track.delete(&id);

  u64 *depth = lock_depth.lookup(&id);
  if (!depth)
    return 0;

  struct depth_id did = {
    .id = id,
    .depth = *depth - 1,
  };

  u64 *aq = time_aq.lookup(&id);
  if (!aq)
    return 0;

  int *stackid = stack.lookup(&did);
  if (!stackid)
    return 0;

  u64 cur = bpf_ktime_get_ns();
  //int stackid_ = *stackid;

  time_held.update(&did, &cur);

  return 0;
}

int trace_func_mutex_unlock(struct pt_regs *ctx)
{
  u64 id = bpf_get_current_pid_tgid();
  u64 delta;

  u64 *depth = lock_depth.lookup(&id);

  if (!depth || *depth == 0)
    return 0;

  *depth -= 1;

  struct depth_id did = {
    .id = id,
    .depth = *depth,
  };

  u64 *held = time_held.lookup(&did);
  if (!held)
    return 0;

  int *stackid = stack.lookup(&did);
  if (!stackid)
    return 0;

  u64 cur = bpf_ktime_get_ns();
  delta = cur - *held;

  if (FILTER) {
    lock_key key = {};
    u64 addr = ctx->di;
    key.lock_addr = addr;
    key.pid = id;
    key.wait_latency = delta;
    bpf_get_current_comm(&key.comm, 16);
    key.stack_id = stack_traces.get_stackid((struct pt_regs *)ctx, 0);
    lock_hash.atomic_increment(key);
   }

  stack.delete(&did);
  return 0;
}

#if ENABLE_SCHED
RAW_TRACEPOINT_PROBE(sched_wakeup)
{
  struct task_struct *p = (struct task_struct *)ctx->args[0];
  u32 pid;
  lock_data *lock;

  bpf_probe_read_kernel(&pid, sizeof(pid), &p->pid);

  lock = start.lookup(&pid);
  if (lock == 0)
    return 0;   // missed start

  if (lock->get_ts == 0)
    lock->wake_ts = bpf_ktime_get_ns();
}

/*
RAW_TRACEPOINT_PROBE(sched_waking)
{
  struct task_struct *p = (struct task_struct *)ctx->args[0];
  u32 pid;
  lock_data *lock;

  bpf_probe_read_kernel(&pid, sizeof(pid), &p->pid);

  lock = start.lookup(&pid);
  if (lock == 0)
    return 0;   // missed start

  if (lock->get_ts == 0)
    lock->wake_ts = bpf_ktime_get_ns();
  return 0;
}
*/

/*
RAW_TRACEPOINT_PROBE(sched_wakeup_new)
{
  struct task_struct *p = (struct task_struct *)ctx->args[0];
  u32 pid;
  lock_data *lock;

  bpf_probe_read_kernel(&pid, sizeof(pid), &p->pid);

  lock = start.lookup(&pid);
  if (lock == 0)
    return 0;   // missed start

  lock->wake_ts = bpf_ktime_get_ns();
}

RAW_TRACEPOINT_PROBE(sched_switch)
{
  struct task_struct *next= (struct task_struct *)ctx->args[2];
  struct task_struct *prev = (struct task_struct *)ctx->args[1];
  u32 pid, prev_pid;
  lock_data *lock;
  long state;

  bpf_probe_read_kernel(&pid, sizeof(next->pid), &next->pid);
  bpf_probe_read_kernel(&prev_pid, sizeof(prev->pid), &prev->pid);

  //if (prev->STATE_FIELD == TASK_RUNNING) {
  //}

  lock = start.lookup(&pid);
  if (lock == 0) {
    //lock = start.lookup(&pid);
    //bpf_probe_read_kernel(&state, sizeof(long), (const void *)&prev->STATE_FIELD);
    //if (lock == 0)
      return 0;
  }

  lock->wake_ts = bpf_ktime_get_ns();
}
*/
#endif

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
parser.add_argument("-t", "--type-ms", type=str, dest="type",
  help="mutex/rwsem/per_rwsemu")

args = parser.parse_args()

if args.min_ms:
  bpf_text = bpf_text.replace('FILTER', 'delta >= %ld' % (args.min_ms * 1000000))
else:
  bpf_text = bpf_text.replace('FILTER', '1')

if args.lock:
  print("enable sched latency");
  bpf_text = bpf_text.replace('MADDR', ('addr != %s')%args.lock)
  bpf_text = bpf_text.replace('SCHED_TRACE', '1 && lock->wake_ts')
  bpf_text = bpf_text.replace('ENABLE_SCHED', '1')
else:
  print("disable sched latency");
  bpf_text = bpf_text.replace('MADDR', '0')
  bpf_text = bpf_text.replace('SCHED_TRACE', '0')
  bpf_text = bpf_text.replace('ENABLE_SCHED', '0')
  #bpf_text = bpf_text.replace('SCHED_TRACE', '1 && lock->wake_ts')
  #bpf_text = bpf_text.replace('ENABLE_SCHED', '1')

is_support_kfunc = BPF.support_kfunc()
is_run_mode = 0

if is_support_kfunc:
  print("user kfunc", args.type)
  bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
  if args.type == "rwsem_read":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    bpf_text = bpf_text.replace('HOOK_FUNC', "rwsem_down_read_slowpath")
  elif args.type == "rwsem_read_run":
    is_run_mode = 1
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "0")
    bpf_text = bpf_text.replace('HOOK_FUNC', 'rwsem_down_read_slowpath')
  elif args.type == "rwsem_write":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    bpf_text = bpf_text.replace('HOOK_FUNC', "rwsem_down_write_slowpath")
  elif args.type == "rwsem_write_run":
    is_run_mode = 1
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "0")
    bpf_text = bpf_text.replace('HOOK_FUNC', 'rwsem_down_write_slowpath')
  elif args.type == "per_rwsem_read":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    bpf_text = bpf_text.replace('HOOK_FUNC', '__percpu_down_read')
  elif args.type == "per_rwsem_write":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    bpf_text = bpf_text.replace('HOOK_FUNC', 'percpu_down_write')
  elif args.type == "per_rwsem_write_run":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    bpf_text = bpf_text.replace('HOOK_FUNC', 'percpu_down_write')
  elif args.type == "mutex":
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "1")
    #bpf_text = bpf_text.replace('HOOK_FUNC', '__mutex_lock_slowpath')
    bpf_text = bpf_text.replace('HOOK_FUNC', 'mutex_lock')
  elif args.type == "mutex_run":
    print("INFO: mutex run")
    is_run_mode = 1
    bpf_text = bpf_text.replace('NOT_SUPPORT_RUN', "0")
    bpf_text = bpf_text.replace('HOOK_FUNC', '__mutex_lock_slowpath')
    #bpf_text = bpf_text.replace('HOOK_FUNC', 'mutex_lock')
  elif args.type == "per_rwsem_write_run":
    b.attach_kprobe(event="percpu_down_write", fn_name="trace_func_mutex_entry")
    b.attach_kretprobe(event="percpu_down_write", fn_name="trace_func_mutex_return")
    b.attach_kprobe(event="percpu_up_write", fn_name="trace_func_mutex_unlock")
  elif args.type == "throttle":
    b.attach_kprobe(event="throttle_cfs_rq", fn_name="trace_func_throttle")
  else:
    print("not specify the lock type kfunc");
    exit(0)

b = BPF(text=bpf_text)

if not is_support_kfunc:
  bpf_text = bpf_text.replace('ENABLE_FUNC', '0')
  if args.type == "rwsem":
    if not is_support_kfunc:
      b.attach_kprobe(event="down_read", fn_name="trace_func_entry")
      b.attach_kretprobe(event="down_read", fn_name="trace_func_return")
      bpf_text = bpf_text.replace('ENABLE_FUNC', '0')
    else:
      bpf_text = bpf_text.replace('HOOK_FUNC', "down_read")
      bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
  elif args.type == "per_rwsem_read":
    if not is_support_kfunc:
      b.attach_kprobe(event="__percpu_down_read", fn_name="trace_func_entry")
      b.attach_kretprobe(event="__percpu_down_read", fn_name="trace_func_return")
    else:
      bpf_text = bpf_text.replace('HOOK_FUNC', '__percpu_down_read')
      bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
  elif args.type == "per_rwsem_write":
    if not is_support_kfunc:
      b.attach_kprobe(event="percpu_down_write", fn_name="trace_func_entry")
      b.attach_kretprobe(event="percpu_down_write", fn_name="trace_func_return")
    else:
      bpf_text = bpf_text.replace('HOOK_FUNC', 'percpu_down_write')
      bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
  elif args.type == "mutex":
    if not is_support_kfunc:
      b.attach_kprobe(event="mutex_lock", fn_name="trace_func_entry")
      b.attach_kretprobe(event="mutex_lock", fn_name="trace_func_return")
    else:
      bpf_text = bpf_text.replace('HOOK_FUNC', 'mutex_lock')
      bpf_text = bpf_text.replace('ENABLE_FUNC', '1')
  elif args.type == "per_rwsem_write_run":
      b.attach_kprobe(event="percpu_down_write", fn_name="trace_func_mutex_entry")
      b.attach_kretprobe(event="percpu_down_write", fn_name="trace_func_mutex_return")
      b.attach_kprobe(event="percpu_up_write", fn_name="trace_func_mutex_unlock")
  elif args.type == "mutex-run":
      b.attach_kprobe(event="mutex_lock", fn_name="trace_func_mutex_entry")
      b.attach_kretprobe(event="mutex_lock", fn_name="trace_func_mutex_return")
      b.attach_kprobe(event="mutex_unlock", fn_name="trace_func_mutex_unlock")
  elif args.type == "throttle":
      b.attach_kprobe(event="throttle_cfs_rq", fn_name="trace_func_throttle")
  elif args.type == "rwsem-write":
      b.attach_kprobe(event="down_write", fn_name="trace_func_entry")
      b.attach_kretprobe(event="down_write", fn_name="trace_func_return")
  else:
      print("not specify the lock type kprobe");
      exit(0)
else:
  if args.type == "mutex_run":
    print("INFO: mutex run")
    b.attach_kprobe(event="mutex_unlock", fn_name="trace_func_unlock")
  elif args.type == "rwsem_write_run":
    print("INFO: rwsem_write run")
    b.attach_kprobe(event="up_write", fn_name="trace_func_unlock")
  elif args.type == "rwsem_read_run":
    print("INFO: rwsem_read run")
    b.attach_kprobe(event="up_read", fn_name="trace_func_unlock")
  elif args.type == "per_rwsem_write_run":
    print("INFO: per_rwsem_write run")
    b.attach_kprobe(event="percpu_up_write", fn_name="trace_func_unlock")

def print_event(cpu, data, size):
  key = b["events"].event(data)

  #if key.sched_latency < 10000000:
  # return

  print("comm:%s pid:%d addr:%x latency:%ld sched_latency:%ld"%(key.comm, key.pid, key.lock_addr, key.latency, key.sched_latency))
  if key.stack_id > 0:
    kernel_stack = stack_traces.walk(key.stack_id)
    for addr in kernel_stack:
      print(" %-16x %s" % (addr, b.ksym(addr)))

exiting = 0
lock_key = b.get_table("lock_hash")
stack_traces = b.get_table("stack_traces")

print("Tracing start")
#if args.type == "rwsem-stack":
# lock_key = b.get_table("stack_counts")

#b["events"].open_perf_buffer(print_event, page_cnt=64)

report_key=defaultdict(list)

while (1):
  try:
    sleep(10)
    #b.perf_buffer_poll()
  except KeyboardInterrupt:
    exiting = 1

  if 1:
    timestr=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if args.type == "rwsem-stack":
      for k, v in sorted(lock_key.items(),
                 key=lambda lock_key: lock_key[1].value):
        if (v.value > 100):
          #if not k.comm == b'kubelet':
          #  continue

          kernel_stack = stack_traces.walk(k.stack_id)
          for addr in kernel_stack:
            print(" %-16x %s" % (addr, b.ksym(addr)))

          print("%d %s,%d" % (v.value, k.comm, k.pid))
    else:
      for key in lock_key.keys():
        hot_stack=0
        stack_str=""

        #print("comm:%s pid:%d addr:%x latency:%ld sched_latency:%ld"%(key.comm, key.pid, key.lock_addr, key.latency, key.sched_latency))
        #res = os.popen("cat /proc/"+str(key.pid)+"/cgroup | grep cpuset").read()
        #print(res)
        if key.stack_id > 0:
          kernel_stack = stack_traces.walk(key.stack_id)
          for addr in kernel_stack:
            stack_str += "%s,"%((b.ksym(addr).decode()))
            #print("  %-16x %s" % (addr, b.ksym(addr)))
        #if stack_str.find("vm_mmap_pgoff") or stack_str.find("__vm_munmap"):
        #  l_key = "0x%lx"%(0)+","+str(stack_str)
        #else:
        l_key = "%s,%d,%lx"%(key.comm.decode(), key.pid, key.lock_addr)+","+str(stack_str)
        #print("%d,%s: %s latency:%ld"%(key.pid, key.comm,  l_key, key.latency))
        #report_key[l_key] += int(key.latency)
        #report_key[l_key].append(int(key.latency))
        #print("%d,%s: %s latency:%ld"%(key.pid, key.comm,  l_key, key.latency))
        if is_run_mode:
          #print("%s %s wait_latency:%ld run_latency:%ld sched_latency:%ld"%(timestr, l_key, key.wait_latency, key.run_latency, key.sched_latency))
          #report_key["%lx"%key.lock_addr].append("%s %s wait_latency:%ld run_latency:%ld sched_latency:%ld"%(timestr, l_key, key.wait_latency, key.run_latency, key.sched_latency))
          if args.lock:
            report_key["%lx"%key.lock_addr].append("%s %s wait_latency:%ld run_latency:%ld sched_latency:%ld"%(timestr, l_key, key.wait_latency, key.run_latency, key.sched_latency))
          else:
            report_key["%lx"%key.lock_addr].append("%s %s wait_latency:%ld run_latency:%ld sched_latency:-1"%(timestr, l_key, key.wait_latency, key.run_latency))
        else:
          #print("%s %s wait_latency:%ld sched_latency:%ld"%(timestr, l_key, key.wait_latency, key.sched_latency))
          if args.lock:
            report_key["%lx"%key.lock_addr].append("%s %s wait_latency:%ld run_latency:-1 sched_latency:%ld"%(timestr, l_key, key.wait_latency, key.sched_latency))
          else:
            report_key["%lx"%key.lock_addr].append("%s %s wait_latency:%ld run_latency:-1 sched_latency:-1"%(timestr, l_key, key.wait_latency))
        #else:
        #print("%s %s time:%ld "%(timestr, l_key, key.latency))
    if 0:
      sorted_items = sorted(report_key.items(), key=lambda item: item[1], reverse=True)
      for i in range(len(sorted_items)):
        print(sorted_items[i])
    if 0:
      for key in report_key.keys():
        print("%s %s cnt:%ld avg:%ld min:%ld max:%ld"%(timestr, key, len(report_key[key]), sum(report_key[key])/len(report_key[key]), min(report_key[key]), max(report_key[key])))
    if 1:
      for key in report_key.keys():
        print("lockaddr:%s"%(key))
        for item in report_key[key]:
          print("   %s"%item)

  lock_key.clear()
  report_key.clear()

  if exiting:
    print("Detaching...")
    exit()
