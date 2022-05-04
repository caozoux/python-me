#ifndef __BCC_SCHED_SWITCH__
#define __BCC_SCHED_SWITCH__
#include<include/bcctype.h>

typedef struct {
	u64 __unused__;
	char prev_comm[16];
	pid_t prev_pid;
	int prev_prio;
	long prev_state;
	char next_comm[16];
	pid_t next_pid;
	int next_prio;
} sched_switch_data;

#endif
