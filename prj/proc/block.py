#!/bin/python3

import os

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--device", type="string", dest="device",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()

SYS_BLOCK="/sys/kernel/debug/block"
SYS_DEVICE=""
SYS_DEVICE_QUEUE_ITER="/hctx"

def block_queue_read(dpath, name):
        return open(dpath+name,'r').read()

queue_item={"active","busy","ctx_map","dispatch","dispatch_busy","dispatched","flags","io_poll","queued","run","sched_tags","sched_tags_bitmap","state","tags","tags_bitmap","type"}
def check_block_queue(blockdev):
    hw_queue = 0
    queue_path=blockdev+"/hctx"

    for i in range(512):
        if not os.path.exists(blockdev+"/hctx"+str(i)):
            break
        hw_queue += 1
    
    for i in range(hw_queue):
        queue_dir=blockdev+SYS_DEVICE_QUEUE_ITER+str(i)+"/";
        for name in queue_item:
            res=block_queue_read(queue_dir, name)
            print("=======>",name,":", res)
        #dispatch= block_queue_read(queue_dir, "dispatch")
        #queued = block_queue_read(queue_dir, "queued")
        #run = block_queue_read(queue_dir, "run")
        #run = block_queue_read(queue_dir, "run")
        #print(dispatch, queued,run)

    
if options.device:
    SYS_DEVICE=os.path.join(SYS_BLOCK, options.device)
    if not os.path.exists(SYS_DEVICE):
       print("ERR:",SYS_DEVICE, "not find")

    check_block_queue(SYS_DEVICE)



