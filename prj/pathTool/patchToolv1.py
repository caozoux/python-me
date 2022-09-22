#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from pyme  import mfiles
from pyme  import mfiles;
from pyme  import patchop;
from optparse import OptionParser;
#from patch import patchbase;
import multiprocessing;
import colorprint;
import os;
import re;

#static command function
stCmdList={
# 格式化处理
"format":"patchFormat.py",
# am 处理
"am":"patchAm.py",
# merge 处理
"merge":"patchMerge.py",
#分析冲突补丁
"an":"patchAnsyl.py",
}

parser = OptionParser()
parser.add_option("-e", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all commands") 
(options, args) = parser.parse_args()

if options.list:
    for key in stCmdList:
        print("%+8s        %s"%(key, stCmdList[key]))
print("key", end="");


