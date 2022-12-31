bpftrace --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/dcache.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/fs.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/path.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/uio.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/writeback.h \
-e 'kprobe:__writeback_single_inode
{
  $c=((struct inode *)arg0)->i_sb->s_id;
  $d=((struct inode *)arg0)->i_ino;
  printf("%d %s %s %d\n",pid, comm, $c, $d);
}'
