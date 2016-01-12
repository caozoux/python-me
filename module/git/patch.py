#!/usr/bin/env python

import os
import sys,time
import subprocess
from clrpr import clrprt



def runcmd(cmd, cmdshow=0):
    if cmdshow:
        print(cmd)
    return os.popen(cmd).read()

def patch_get_title(patch_name):
    ""
    title_name1=runcmd("sed -n '4p' "+patch_name+"  | cut -b 18-")
    title_name2=runcmd("sed -n 'p' "+patch_name)
    if titile_name2 == "":
	title_name=title_name1
    else:
        title_name=title_name1+title_name2

    return title_name

def patch_get_commit(patch_name):
    var=runcmd("sed -n '5p' "+patch_name)

    commit_start_cnt = 5
    commit_end_cnt=runcmd("cat "+patch_name+" | grep -n "\-\-\-$" | cut -d : -f 1")
    if var != "":
        commit_start_cnt += 1

    runcmd(" sed -n '" + str(commit_start_cnt) +",", str(commit_end_cnt)+"p' "+ patch_name +"  | grep -n "^$"| cut -d : -f 1")


