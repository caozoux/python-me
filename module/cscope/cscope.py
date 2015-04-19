#!/usr/bin/env python3.4

import os
import sys,time
import subprocess
from clrpr import clrprt
from base import oslc

def setup_filelist(dir,src):
    "follow the *.o file, then setup the file list"
    cmd="cd "+dir+"; find -name \"*.o\"; cd -";
    out=os.popen(cmd)
    print(cmd)
    for line in out.readlines():
        #filename=src+"/"+line[:-2]+"c"
        filename=src+line[:-2]+"c"
        if os.path.exists(filename):
            cmd="echo "+filename+" >> cscope.files"
            print(filename)
            os.system(cmd);
    os.system("cscope -bq")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("argments is less")
        exit()
    dir = sys.argv[1]
    src = sys.argv[2]
    #example ~/bin/module/cscope/cscope.py  /export/ti/out_kernel-3.14.x/ /export/ti/kernel-3.14.x/
    setup_filelist(dir,src)
