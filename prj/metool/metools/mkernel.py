import os
import re
import json
import subprocess
import random
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--show_template", action="store_true", dest="template",
                  help="--cmd stat_event ")
parser.add_option("-t", "--type", type="string", dest="type",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-c", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
(options, args) = parser.parse_args()

vmenv={
"ip":"vm"
}

mekerneldict={
"srcdir":"~/github/cloud-kernel",
"builddir": "~/github/cache/cloud-kernel",
"image":"arch/x86/boot/bzImage",
}

mekernelcmddict={
"build_bzImage":"make O=args1 bzImage -j args2",
"build_all":"make O=args1 -j args2",
"install_bzImage":"make O=args1 install -j args2",
"install_all_into_vm":"arch/x86/boot/bzImage",
"install_bzImage_into_vm":"arch/x86/boot/bzImage",
}

mejsonfile={
"kernel":mekerneldict,
"vmenv":vmenv,
"command":mekernelcmddict,
}

def LoadMachineJson(file=""):
    if file == "":
        file ="~/.metooljson"

def ListCommand():
    for key in mejsonfile:
        for k2 in mejsonfile[key]:
            print(("%s%--10s%--30s%--30s")%("config:", key, k2, mejsonfile[key][k2]))
            #print(("%s%--10s%--20s%--20s")("config:",key, k2, mejsonfile[key][k2]))
        #print(key, mejsonfile[key])

def RunCommand():

if options.template:
    benchmarkjson=json.dumps(mejsonfile, ensure_ascii=False,indent=2)
    print(benchmarkjson)

if options.list:
    ListCommand()

if options.cmd:
    if options.type:
        RunCommand(options.type)
