#!/usr/bin/env python3.4

import os
import sys,time
import subprocess

def runcmd(cmd, cmdshow=0):
    if cmdshow:
        print(cmd)
    return os.popen(cmd).read()


def subcmd(cmd):
    p=subprocess.Popen(cmd, stdin = subprocess.PIPE, \
        stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
    p.wait()
    #git apply fail
    if p.returncode:
        errout=p.stderr.read()
        print(errout)
        return 1
    else:
        return 0
