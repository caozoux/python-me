#!/usr/bin/python3

from __future__ import print_function
from bpfcc import BPF

from collections import defaultdict
import argparse
from time import sleep, strftime

bpf_text = """
#include <linux/mm.h>

typedef struct {
	u64 pid;
	u64 next_pid;
	char task[16];
	u64 delta_us;
	u64 nr_running;
	int stack_id;
} data_t;

struct cfs_rq_partial {
	struct load_weight load;
	unsigned int nr_running, h_nr_running;
};

BPF_PERF_OUTPUT(events);
BPF_HASH(start, u32);
BPF_STACK_TRACE(stacks, 2048);

RAW_TRACEPOINT_PROBE(sched_switch)
{
	u32 pid;
	u32 prev_pid, next_pid;
	long prev_state, next_state;
	u64 *tsp, delta_us;
	struct task_struct *prev = (struct task_struct *)ctx->args[1];
	struct task_struct *next = (struct task_struct *)ctx->args[2];
	u64 ts = bpf_ktime_get_ns();
	int len;

	struct cfs_rq_partial *my_q = NULL;

	bpf_probe_read_kernel(&prev_state, sizeof(long), (const void *)&prev->__state);
	bpf_probe_read_kernel(&prev_pid, sizeof(prev->pid), &prev->pid);

	bpf_probe_read_kernel(&next_state, sizeof(long), (const void *)&next->__state);
	bpf_probe_read_kernel(&next_pid, sizeof(next->pid), &next->pid);

	if (FILTER_PREV_PID)
		return 0;

	if (FILTER_NEXT_PID)
		return 0;

/*
	if (!(FILTER_PID)) {
		start.update(&pid, &ts);
	}

	bpf_probe_read_kernel(&pid, sizeof(prev->pid), &prev->pid);

	if ((FILTER_PID))
		return 0;

	if (prev->__state != 0)
		return 0;

	tsp = start.lookup(&pid);
	if (tsp == 0) {
		return 0;   // missed enqueue
	}
	delta_us = (bpf_ktime_get_ns() - *tsp) / 1000;
	start.delete(&pid);

	my_q = (struct cfs_rq_partial *)next->se.cfs_rq;
	len = my_q->nr_running;
*/

	data_t data = {};
	data.pid = prev_pid;
	data.next_pid = next_pid;
	bpf_probe_read_kernel(&data.next_pid, sizeof(next->pid), &next->pid);
	data.delta_us = 0;
	data.nr_running = 0;
	data.stack_id = stacks.get_stackid(ctx, 0);
	bpf_probe_read_kernel_str(&data.task, sizeof(data.task), prev->comm);
	events.perf_submit(ctx, &data, sizeof(data));

	return 0;
}

"""

examples = """examples:
	-i  interval milliseconds
"""

parser = argparse.ArgumentParser(
	description="Trace lock sched latency",
	formatter_class=argparse.RawDescriptionHelpFormatter,
	epilog=examples)

parser.add_argument("-p", "--pid", type=int, dest="pid",
	help="monitor specify pid switch time")
parser.add_argument("-s", "--stack", action="store_true", dest="stack",
	help="print kstack")
parser.add_argument("-m", "--mode", type=str, dest="mode",
	help="mode sleep/run")

args = parser.parse_args()

if args.mode:
	if not args.pid:
		print("Err: not task pid")
		exit(1)

	if args.mode == "sleep":
		bpf_text = bpf_text.replace('FILTER_PREV_PID', 'prev_pid != %s' % args.pid)
		bpf_text = bpf_text.replace('FILTER_NEXT_PID', 'prev_state == 0')
	elif args.mode == "run":
		bpf_text = bpf_text.replace('FILTER_PREV_PID', 'prev_pid != %s' % args.pid)
		bpf_text = bpf_text.replace('FILTER_NEXT_PID', 'prev_state != 0')
    else:
		bpf_text = bpf_text.replace('FILTER_PREV_PID', 'prev_pid != %s' % args.pid)
		bpf_text = bpf_text.replace('FILTER_NEXT_PID', 'prev_state == 0')

def print_stack(stack_id):
	stack_traces = b.get_table("stacks")
	kernel_stack = []
	if stack_id > 0:
		kernel_tmp = stack_traces.walk(stack_id)

		# fix kernel stack
		for addr in kernel_tmp:
			kernel_stack.append(addr)
		for addr in kernel_stack:
			print("	%s" % b.ksym(addr))

def print_event(cpu, data, size):
	event = b["events"].event(data)
	print("%-8s %-16s %-6s %-6s %14s %d" % (strftime("%H:%M:%S"), event.task, event.pid, event.next_pid, event.delta_us, event.nr_running))
	if args.stack:
		print_stack(event.stack_id)

b = BPF(text=bpf_text)

print("start trace..\n")
b["events"].open_perf_buffer(print_event, page_cnt=64)
while 1:
	try:
		b.perf_buffer_poll()
	except KeyboardInterrupt:
		exit()

