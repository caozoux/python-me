bpftrace --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/dcache.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/fs.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/path.h \
        --include  /usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/uio.h \
-e 'kprobe:ext4_file_write_iter
{
  $n=((struct kiocb *)arg0)->ki_filp->f_inode->i_sb->s_id;
  $d=str(((struct kiocb *)arg0)->ki_filp->f_path.dentry->d_name.name);
  $c=((struct iov_iter *)arg1)->count;
  if ($n == "sda2") {
    printf("%s %s %d\n", $n, $d, $c);
  }
}'
