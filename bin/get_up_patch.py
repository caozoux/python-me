#!/usr/bin/env python3.4
import os
import sys,time
from base  import osme
from git import gitApp


patch_src="/home/wrsadmin/github/linux-stable"

if len(sys.argv) <= 1:
    print("please input the commit number")
    exit()

commit_id = sys.argv[1]

cur_dir=osme.runcmd("pwd")
out = osme.runcmd("git -C "+patch_src+" format-patch -1 "+commit_id+" -o "+cur_dir,1)
if len(out) > 3:
    patch=out[:-1]
    gitApp.format_linuxmail_patch(patch)
    if gitApp.check_patch_format(patch,2):
        exit();
else:
    print("format error\n")
