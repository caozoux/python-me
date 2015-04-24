#!/usr/bin/env python3.4
import os
import sys,time
import signal
from base  import osme
from clrpr import clrprt
from git import gitApp

cmdpull="wrgit send-email --to kexin.hao@windriver.com --to yue.tao@windriver.com --cc lpd-eng-rr@windriver.com rr *.patch   --no-chain-reply"

cmdtest="git send-email --to cao.zou@windriver.com rr *.patch --no-chain-reply"

def check_all_patch(dir):
    cmd="ls "+dir[:-1]+"/*.patch"
    print(cmd)
    for line in os.popen(cmd).readlines():
        patchname=line[:-1]
        if os.path.exists(patchname):
            if gitApp.check_patch_format(patchname):
                clrprt.err(patchname+" format error")
                return 1
        else:
            clrprt.err(patchname+" not exist")
            return 1;
    return 0;

def main():
    print("ok:   git send to lpd-eng-rr")
    print("test: git send to lpd-eng-rr")
    print("please input(test/ok):", end="")

    runcmd=""
    while True:
        INPUT=input()
        if INPUT == "ok":
            runcmd=cmdpull

        elif INPUT == "test":
            runcmd=cmdtest
        else:
            print("not support")
            continue;

        if check_all_patch(os.popen("pwd").read()):
            return 1;
        print("are you share to send(Y/n):",end="")
        INPUT=input()
        print(len(INPUT))
        if INPUT== "Y" and INPUT== "y":
            print(cmdtest)
            if os.system(cmdtest):
                clrprt.err("send test email failed")
            else:
                clrprt.info("send test email to cao.zou")
        else:
            return 1;
        return 0;

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("argments is less")
        exit()
    main()
