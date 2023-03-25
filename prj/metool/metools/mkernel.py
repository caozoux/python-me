#!/bin/python3

import os
import sys
import re
import json
import subprocess
import random
from API import api
from optparse import OptionParser

BuildThreadsCount=16
parser = OptionParser()
parser.add_option("-e", "--show_template", action="store_true", dest="template",
                  help="--cmd stat_event ")
parser.add_option("-t", "--type", type="string", dest="type",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-c", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run command")
(options, args) = parser.parse_args()

vmenv={
"ip":"vm"
}

mekerneldict={
"srcdir":"/home/zc/github/cloud-kernel",
"builddir": "/home/zc/github/cache/cloud-kernel",
"image":"arch/x86/boot/bzImage",
"version": "include/config/kernel.release",
"vm_vmlinux_path": "root@vm:/boot/vmlinuz-4.19.91+",
}


mekernelcmddict={
"build_bzImage":"''.join(['make O=', mekerneldict['builddir'], ' bzImage  -j32 '])",
"build_all":"''.join(['make O=', mekerneldict['builddir'], ' -j32 '])",
"install_bzImage":"''.join(['scp ', mekerneldict['builddir'],'/', mekerneldict['image'], ' ', mekerneldict['vm_vmlinux_path']])",
"install_modules":"''.join(['make O=', mekerneldict['builddir'], '  modules_install  INSTALL_MOD_PATH=', mekerneldict['builddir'],'/modules'])",
"vm_restart":"''.join(['ssh root@vm \"shutdown -r 0\"'])",
}

mejsonfile={
"kernel":mekerneldict,
"vmenv":vmenv,
"command":mekernelcmddict,
}

def RunCommand(name):
    name=name.replace(" ","")
    name=name.split("+")
    for item in name:
        cmd=eval(mekernelcmddict[item])
        print(item,cmd)
        ret=api.excuteCommand(cmd, stdshow=1)
        if ret != 0:
            return

def GetVersion():
    versionfile = os.path.join(mekerneldict['builddir'],mekerneldict['version'])
    version=api.FileRead(versionfile)
    print(version,versionfile)

def LoadMachineJson(file=""):
    if file == "":
        file ="~/.metooljson"

def ListAll():
    for key in mejsonfile:
        for k2 in mejsonfile[key]:
            print(("%s%--10s%--30s%--30s")%("config:", key, k2, mejsonfile[key][k2]))

def ListCommand():
    print("You can run this commands by '-r':")
    for key in mejsonfile["command"]:
        print(("%++13s  %--20s%--30s")%("command:", key, eval(mejsonfile["command"][key])))

if len(sys.argv) == 1:
    parser.print_help()
    
if os.path.exists(os.path.expanduser("~/.mkernel.json")):
    mekerneldict=api.DumpJsonByFilename("~/.mkernel.json")

if options.template:
    benchmarkjson=json.dumps(mejsonfile, ensure_ascii=False,indent=2)
    print(benchmarkjson)

if options.list:
    ListCommand()

if options.run:
    RunCommand(options.run)
#print((mekernelcmddict["build_all"]))
#print(eval(mekernelcmddict["build_all"]))
#GetVersion()
