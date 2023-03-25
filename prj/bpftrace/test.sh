#!/usr/bin/bpftrace
	
#include <linux/fs.h>
#include <linux/dcache.h>
kprobe:vfs_unlink
{
  $d=str(((struct dentry *)arg1)->d_name.name);
  printf("%s\n", $d);
}
