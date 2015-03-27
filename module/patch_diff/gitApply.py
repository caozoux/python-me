#!/usr/bin/env python

import os
import sys,time
import subprocess
from clrpr import clrprt

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

def get_linuxmail_patch(patchname,maildir,  curdir="", cmp_upstream="\[ Upstream commit "):
    "throught the patchname, then get the same patch \
    through kernle mailline. \
    argments: \
        patchname: the patch name \
        maildir: the mailline dir \
        curdir: the format patch out"

    #get the commit id in upstream
    if curdir=="":
        cmd="pwd"
        curdir=os.popen(cmd).read()
    
    retstr=""
    upstream_commit_num=0
    commitid=""
    cmd="cat "+patchname+" | grep \""+cmp_upstream+"\""
    cmdout=os.popen(cmd)
    for line in cmdout.readlines():

        if line == "":
            if upstream_commit_num==0:
                return "";
            else:
                if upstream_commit_num>1:
                    clrprt.printc("patch: "+patchname+" need your check")
                    return ""
                else:
                    return retstr
        else:
            commitid=line[18:-3]
            #clrprt.printc(commitid)
            cmd="cd "+maildir+"; "+"git show "+commitid
            cmdout1=os.popen(cmd).read()
            upstream_commit_num += 1
            cmd="cd "+maildir+"; "+"git format-patch -1 "+commitid+" -o "+curdir
            #print(cmd)
            retstr=os.popen(cmd).read()

    return retstr

def format_linuxmail_patch(patchname):
    "add  commit $commit upstream \
     to mailpatch"
    commitid=""

    #patch need to format
    cmd="sed -n 6p "+patchname
    cmdout=os.popen(cmd).read()
    if cmdout[:6] == "commit":
        clrprt.printc(patchname+" is formated, please check")
        return 
    
    cmd="sed -n 7p "+patchname
    cmdout=os.popen(cmd).read()
    if cmdout[:6] == "commit":
        clrprt.printc(patchname+" is formated, please check")
        return 

    #get patch commit id
    cmd="sed -n 1p "+patchname
    cmdout=os.popen(cmd).read()
    commitid=cmdout[6:46]

    cmd="sed -n 5p "+patchname
    cmdout=os.popen(cmd).read()

    print(len(cmdout))
    if len(cmdout)==1:
        #sed -i '5 acommit 5bb9cbaa622a2bbde8e307d4e0528dd2c8212a6a upstream\n'
        cmd="sed -i '5 acommit "+commitid+" upstream\\n'"+" "+patchname
        #print(cmd)
        if os.system(cmd):
            clrprt.printc(cmd+" is failed")
    else:
        cmd="sed -i '6 acommit "+commitid+" upstream\\n'"+" "+patchname
        #print(cmd)
        if os.system(cmd):
            clrprt.printc(cmd+" is failed")

def git_apply(patchname,src,dst):
    "git apply the patchname, if success, return 0"

    if not os.path.exists(patchname):
        print(patchname+" isn't exist")
        return 1

    patch_src=src
    patch_dst=dst

    cmd="cat "+patchname+" | grep \"+++ \""+" | cut -b 7-"
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
    #git apply fail
    if p.returncode:
        errout=p.stderr.read()
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
