bpftrace --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/dcache.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/fs.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/path.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/uio.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/writeback.h \
-e 'kprobe:ext4_writepages
{
  $c=((struct writeback_control *)arg1)->nr_to_write;
  printf("%d %s write %d\n",pid, comm, $c);
}'
