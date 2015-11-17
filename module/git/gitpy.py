#!/usr/bin/env python

import os
import sys,time
import subprocess
from clrpr import clrprt
from git import gitApp

if __name__ == "__main__":
    rootdir = sys.argv[1]
    cmdout = os.popen("ls "+rootdir+" | sort ")
    for line in cmdout.readlines():
        print(line[:-1])

        filename = rootdir+"/"+line[:-1]
        if not os.path.exists(filename):
            clrprt.printc(filename+" no find");
            continue
        #clrprt.printc(filename);
        cmd="cat "+filename+" | grep \"+++ \""+" | cut -b 7-"
        target_dir="/export/disk1T1/bsp_work/IOT-REV2/git/git.freescale.com.ppc.sdk.linux"

        modify_file_num = 0
        modify_file_invalid = 0
        for line1 in os.popen(cmd).readlines():
            modify_file_num += 1
            modify_file = line1[:-1]
            #print(line1[:-1])
            if modify_file [-2:] == ".c":
                target_file = target_dir+"/"+ modify_file[:-1]+"o"
                if not os.path.exists(target_file):
                    modify_file_invalid += 1
                    print(target_file+ " no exist")
                else:
                    print(target_file+ " find")
        if modify_file_num == modify_file_invalid:
            clrprt.printc(filename+" can del");
            os.system("rm "+filename)


        print("")
