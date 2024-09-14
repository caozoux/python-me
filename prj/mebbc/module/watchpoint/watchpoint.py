bpftrace -e 'watchpoint:0xff4f31c080fae1c8:8:w { @[kstack] = count(); } interval:s:60 { time("%H:%M:%S\n"); print(@); clear(@); }'  
