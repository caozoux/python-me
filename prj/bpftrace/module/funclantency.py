#!/bin/bpftrace

kprobe:cgroup_rmdir
{
	@start[tid] = nsecs;
}

kretprobe:cgroup_rmdir /@start[tid] != 0/ 
 {
	$delta = nsecs - @start[tid];
        //@loip[ksym(reg("ip"))] = count();
	if ( $delta > 1000000)
	{
		@stack[kstack()]=count();
	}
	@nsecst = hist((($delta)));
	delete(@start[tid]);
}
