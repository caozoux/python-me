#!/usr/bin/env python3.4
import os
import sys,time
import gitApply

patch_src="/export/disk1T1/bsp_work/TI_AM335X/TI_SDK/SDK8/board-support/linux-3.14.26-g2489c02/"
patch_dst="/export/disk1T1/bsp_work/TI_AM335X/kernel-3.14.x/"

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
    #time.sleep(1)
    print(patchname)

    #git am successfully
    if not gitApply.git_apply(patchname,patch_src, patch_dst):
        os.system("mv "+patchname+ " apply_src")
    else:
        print(patchname+ "： git apply failed")
        #exit()
        

        

