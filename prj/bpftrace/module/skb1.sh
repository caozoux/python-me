#!/usr/bin/bpftrace
#include </usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/linux/skbuff.h>
#include </usr/src/kernels/4.18.0-2.4.3.3.kwai.x86_64/include/net/sock.h>

BEGIN {
}
kprobe:tcp_rcv_established /cpu == 22/ 
{ 
  $k=(struct sock*) arg0;
  $s=(struct sk_buff *) arg1;
  @sklen=hist($s->len);
  @socketcnt[$k] +=  1;
  @socket[$k] +=  $s->len;
  @socketavg[$k] =  @socket[$k]/@socketcnt[$k];
  //printf("len:%ld\n", $s->len);
}

//kprobe:__netif_receive_skb_core /cpu == 22/ 
kprobe:ip_rcv /cpu == 22/ 
{ 
  $s=(struct sk_buff *) arg0;
  @sklen=hist($s->len);
  //printf("len:%ld\n", $s->len);
}

kretprobe:tcp_recvmsg /cpu == 22/ 
{ 
  @recvmsg=hist(retval);
}

kretprobe:dev_gro_receive /cpu == 22/ 
{ 
  if ( retval == 1 )
  {
    @merge += 1;
  }
  @recv += 1;
}

interval:s:2
{
  @diff_recv = @recv - @old_recv;
  @old_recv = @recv;
  @diff_merge = @merge - @old_merge;
  @old_merge = @merge;
  printf("%d %d\n", @diff_recv, @diff_merge);
  exit()
}

END {
  #clear(@socketcnt);
  clear(@socket);
}
