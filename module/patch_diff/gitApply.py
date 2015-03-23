#!/usr/bin/env python

import os
import sys
import subprocess

#patch_src="/extend/disk1G1/work/ti-am334x/ti-linux-kernel/"
#patch_dst="/extend/disk1G1/work/ti-am334x/kernel-3.14.x/"
#global patch_src
#global patch_dst

def path_modefy_files(filename):
    "print the modefy files in one patch"
    if not os.path.exists(filename):
        return
    cmd="cat "+filename+" | grep \"+++ \""+" | cut -b 7-"
    cmdout=os.popen(cmd).read()
    print(cmdout)

def cmp_file(filename,src,dst):
    "cmp the file,if the same, return 0"
    src_file=src+filename
    dst_file=dst+filename
    if os.path.exists(src_file) and os.path.exists(dst_file):
        cmd="diff -q "+src_file+" "+dst_file
        print("           "+cmd)
        cmdout=os.popen(cmd).read()
        if not cmdout =="":
            return 1
        else:
            return 0
    return 1

def git_apply(patchname,src,dst):
    "git apply the patchname, if success, return 0"

    if not os.path.exists(patchname):
        print(patchname+" isn't exist")
        return 1

    patch_src=src
    patch_dst=dst

    #print(patch_dst)
    #print(patch_src)
    #exit()
    cmd="cat "+patchname+" | grep \"+++ \""+" | cut -b 7-"
    #cmdout=os.popen(cmd).read()
    #print(cmdout)
    cmdout=os.popen(cmd)
    files_num=0
    samefile_num=0
    for line in cmdout.readlines():
        filename=line[:-1]
        #file is deferent
        if not cmp_file(filename,patch_src,patch_dst):
            samefile_num += 1
        files_num += 1

    #the patch no need, because the src and dst is the same
    if files_num == samefile_num:
        print(patchname+" no need, the file is the same")
        return 2

    cmd="git apply "+patchname
    p=subprocess.Popen(cmd, stdin = subprocess.PIPE, \
        stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    p.wait()
    if p.returncode:
        errout=p.stderr.read()
        #print(p.stderr.read())
        print(errout)
        
        return 1
    else:
        print(patchname+" apply successfully")
        return 0

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("argments is less")
        exit()

    patchname=sys.argv[1]
    git_apply(patchname,src, dst)
