#!/usr/bin/env python
import os
import sys
import subprocess


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

def cmd_dir(src,dst):
    if os.path.exists(dst) and os.path.exists(src):
        pass
    else:
        print(src+" or "+dst+" it isn't exist") 
        return

    cmd="find "+src 
    cmdout=os.popen(cmd)
    for line in cmdout.readlines():
        file=line[:-1]
        dstfile=dst+"/"+file
        if os.path.exists(dstfile):
            if not cmp_file(file,src,dst):
                print(file+" isn't the same")
        else:
            print(file+" isn't exit in "+dst)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("argments is less")
        exit()

    src=sys.argv[1]
    dst=sys.argv[2]
    if os.path.exists(dst) and os.path.exists(src):
        pass
    else:
        print("it isn't exist") 
        exit()

    cmd_dir(src,dst)

