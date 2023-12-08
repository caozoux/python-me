#!/usr/bin/bpftrace

#include <linux/fs.h>
#include <linux/dcache.h>
kprobe:do_unlinkat
{
  $d=str(((struct dentry *)arg1)->d_name.name);
  if ( $d == "kess" ) {
  }
  printf("pid:%d comm:%s dir:%s\n", pid, comm, $d);
}
