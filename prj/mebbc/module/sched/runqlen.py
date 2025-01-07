#!/usr/bin/python3

from __future__ import print_function
from bpfcc import BPF, PerfType, PerfSWConfig
from time import sleep, strftime
from tempfile import NamedTemporaryFile
from os import open, close, dup, unlink, O_WRONLY
import multiprocessing
import argparse
from collections import defaultdict

# arguments
examples = """examples:
  ./runqlen     # summarize run queue length as a histogram
  ./runqlen 1 10     # print 1 second summaries, 10 times
  ./runqlen -T 1     # 1s summaries and timestamps
  ./runqlen -O     # report run queue occupancy
  ./runqlen -C     # show each CPU separately
"""
parser = argparse.ArgumentParser(
  description="Summarize scheduler run queue length as a histogram",
  formatter_class=argparse.RawDescriptionHelpFormatter,
  epilog=examples)
parser.add_argument("-T", "--timestamp", action="store_true",
  help="include timestamp on output")
parser.add_argument("-O", "--runqocc", action="store_true",
  help="report run queue occupancy")
parser.add_argument("-C", "--cpus", action="store_true",
  help="print output for each CPU separately")
parser.add_argument("-l", "--lc", action="store_true",
  help="only caculate the lc task nr_running")
parser.add_argument("-a", "--cpuarray",
  help="runq cpu mask")
parser.add_argument("interval", nargs="?", default=99999999,
  help="output interval, in seconds")
parser.add_argument("count", nargs="?", default=99999999,
  help="number of outputs")
parser.add_argument("--ebpf", action="store_true",
  help=argparse.SUPPRESS)
args = parser.parse_args()
countdown = int(args.count)
debug = 0
frequency = 99

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

// Declare enough of cfs_rq to find nr_running, since we can't #import the
// header. This will need maintenance. It is from kernel/sched/sched.h:
struct cfs_rq_partial {
  struct load_weight load;
  unsigned long runnable_weight;
  unsigned int nr_running;
  unsigned int h_nr_running;
  unsigned int h_nr_uninterruptible;
  unsigned int nr_nor_running;
  unsigned int nr_lc_running;
  unsigned int nr_be_running;
  atomic_t nr_wake_hint;
  u64 exec_clock;
  u64 min_vruntime;
  u64 min_be_vruntime;
  unsigned int forceidle_seq;
  u64 min_vruntime_fi;
  struct rb_root_cached tasks_timeline;
  struct rb_root_cached be_timeline;
  struct sched_entity *curr;
  struct sched_entity *next;
  struct sched_entity *last;
  struct sched_entity *skip;
  unsigned int nr_spread_over;
  long: 32;
  long: 64;
  long: 64;
  long: 64;
  struct sched_avg avg;
  struct {
    raw_spinlock_t lock;
    int nr;
    long unsigned int load_avg;
    long unsigned int util_avg;
    long unsigned int runnable_sum;
    long unsigned int prio_load_avg;
    long unsigned int prio_util_avg;
    long: 64;
    long: 64;
  } removed;
  long unsigned int tg_load_avg_contrib;
  long int propagate;
  long int prop_runnable_sum;
  long unsigned int h_load;
  u64 last_h_load_update;
  struct sched_entity *h_load_next;
  struct rq *rq;
};

#if 0
struct rq_partial {
  /* runqueue lock: */
  raw_spinlock_t    __lock;
  unsigned int    nr_running;
  unsigned int    nr_nor_running;
  unsigned int    nr_lc_running;
  unsigned int    nr_be_running;
};
#else
struct rq_partial {
  unsigned int    data0;
  unsigned int    nr_running;
  unsigned int    data1[62];

  struct cfs_rq_partial   cfs;
};
#endif

typedef struct cpu_key {
  int cpu;
  unsigned int nr_running;
} cpu_key_t;
STORAGE

int do_perf_event()
{
  unsigned int len = 0;
  struct task_struct *task = NULL;
  struct cfs_rq_partial *my_q = NULL;
  struct cfs_rq_partial *rq_cfs = NULL;
  struct rq_partial *rq = NULL;

  task = (struct task_struct *)bpf_get_current_task();
  my_q = (struct cfs_rq_partial *)task->se.cfs_rq;

  rq = (struct rq_partial *)my_q->rq;
  rq_cfs = (struct cfs_rq_partial *)&rq->cfs;

  if (LC_RUNNING) {
     len = rq_cfs->nr_lc_running + rq_cfs->nr_nor_running;
  } else {
     len = rq->nr_running;
  }

  STORE

  return 0;
}
"""
arg_cpulist=[]

def parse_cpu_distribution(cpu_input):
  cpu_list = set()  # 使用集合避免重复

  parts = cpu_input.split(',')
  for part in parts:
    if '-' in part:
      start, end = map(int, part.split('-'))
      cpu_list.update(range(start, end + 1))
    else:
      cpu_list.add(int(part))

  return sorted(cpu_list)

def print_histogram(values, bins=10):
  print("%s  : %-10s %-30s"%("runq","count","distribution"))
  if len(values) == 0:
    return

  min_index = min(values.keys())
  max_index = max(values.keys())

  min_value = min(values.values())
  max_value = max(values.values())

  for i in range(min_index, max_index+1):
    if i in values.keys():
      print("%-6d: %-10d | %-30s |"%(i, values[i], '*' * (int(values[i]/max_value*29)+1)))
    else:
      print("%-6d: %-10d | %-30s |"%(i, 0, ' '*30))

  return

def report_runq_occ(dist, show_percpu, cpumask=False):
  cpumask_list=[]
  idle = {}
  queued = {}
  nr_running = {}
  cpumax = multiprocessing.cpu_count()
  runqocc=  0
  idle_cnt = 0

  for c in range(0, cpumax):
    idle[c] = 0
    queued[c] = 0
    nr_running[c] = 0
  if show_percpu:
    runq_dict = defaultdict(dict)
    for c in arg_cpulist:
        runq_dict[c] = defaultdict(int)
  else:
    runq_dict = defaultdict(int)

  if cpumask:
    cpumask_list = arg_cpulist
  else:
    for c in range(0, cpumax):
      cpumask_list.append(c)

  for k, v in dist.items():
    #k.cpu,k.nr_running v.value: 表示cpu出现nr_running指定长度的次数
    #如:k.cpu,k.nr_running,v.value = 3, 2 , 15, 表示cpu3在采样周期内
    #   出现nr_running = 2的次数为15次
    if k.nr_running:
      queued[k.cpu] += v.value
      nr_running[k.cpu] += (k.nr_running-1) * (k.nr_running-1) * v.value
      if k.cpu in cpumask_list:
        if show_percpu:
          cpu_runq_d = runq_dict[k.cpu]
          cpu_runq_d[k.nr_running] += v.value
        else:
          runq_dict[k.nr_running] += v.value
    else:
      idle[k.cpu] += v.value

  if show_percpu:
    for c in cpumask_list:
      samples = idle[c] + queued[c]
      if samples:
        runqocc = float(nr_running[c])
      else:
        runqocc = 0
      print("runq load, CPU %-3d %6.2f" % (c, runqocc))
  else:
      if args.cpuarray:
        for c in arg_cpulist:
          runqocc += nr_running[c]
          idle_cnt += idle[c]
      else:
        for c in range(0, cpumax):
          runqocc += nr_running[c]
          idle_cnt += idle[c]

      print("idle: %0.2f latency: %0.2f" % (float(idle_cnt)/100, float(runqocc)))
      sorted_by_value = dict(sorted(runq_dict.items(), key=lambda item: item[0]))
      print_histogram(sorted_by_value)

if args.cpuarray:
  arg_cpulist=parse_cpu_distribution(args.cpuarray)

# code substitutions
bpf_text = bpf_text.replace('STORAGE',
'BPF_HASH(dist, cpu_key_t);')
bpf_text = bpf_text.replace('STORE', 'cpu_key_t key = {.nr_running = len}; ' +
'key.cpu = bpf_get_smp_processor_id(); ' +
'dist.increment(key);')

if args.lc:
  bpf_text = bpf_text.replace('LC_RUNNING', '1')
else:
  bpf_text = bpf_text.replace('LC_RUNNING', '0')

if debug or args.ebpf:
  print(bpf_text)
  if args.ebpf:
    exit()

# initialize BPF & perf_events
b = BPF(text=bpf_text)
b.attach_perf_event(ev_type=PerfType.SOFTWARE,
  ev_config=PerfSWConfig.CPU_CLOCK, fn_name="do_perf_event",
  sample_period=0, sample_freq=frequency)

print("Sampling run queue length... Hit Ctrl-C to end.")

# output
exiting = 0 if args.interval else 1
dist = b.get_table("dist")
cpumax = multiprocessing.cpu_count()
while (1):
  try:
    sleep(int(args.interval))
  except KeyboardInterrupt:
    exiting = 1

  print()
  if args.timestamp:
    print("%-8s\n" % strftime("%H:%M:%S"), end="")

  if args.runqocc:
    runqocc=0
    if args.cpus:
      if args.cpuarray:
        report_runq_occ(dist, True, True)
      else:
        report_runq_occ(dist, True, False)
    else:
      if args.cpuarray:
        report_runq_occ(dist, False, True)
      else:
        report_runq_occ(dist, False, False)
  else:
    # run queue length histograms
    dist.print_linear_hist("runqlen", "cpu")

  dist.clear()

  countdown -= 1
  if exiting or countdown == 0:
    exit()
