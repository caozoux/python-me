#!/usr/bin/env python
import os
import sys,time
import gitApply

patch_src="/extend/disk1G1/work/ti-am334x/ti-linux-kernel/"
patch_dst="/extend/disk1G1/work/ti-am334x/kernel-3.14.x/"

if len(sys.argv) <= 1:
    print("argments is less")
    exit()

patchdir=sys.argv[1]

if not os.path.exists(patchdir):
    print(patchname+" isn't exist")
    exit()
    
cmd="find "+patchdir+" -name \"*.patch\" | sort "
#cmdout=os.popen(cmd).read()
#print(cmdout)
cmdout=os.popen(cmd)

for line in cmdout.readlines():
    patchname = line[:-1]
    time.sleep(1)
    print(patchname)

    #git am successfully
    if not gitApply.git_apply(patchname,patch_src, patch_dst):
        os.system("mv "+patchname+ " apply_suc")
        

        

