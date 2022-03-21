import os
import re
import json
import subprocess
import random
from API import api
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run command")
parser.add_option("-s", "--sub", type="string", dest="sub",
                  help="--sub  proc name")
parser.add_option("-m", "--memory", type="string", dest="memory",
                  help="--memory specify the memory cgroup name")
(options, args) = parser.parse_args()

def CgMemStat():
    pagetype_list=['active_anon', 'inactive_anon','active_file','inactive_file']
    memtype_list=['rss', 'cache']
    cgmemproc=os.path.join("/sys/fs/cgroup/memory", options.memory, "memory.stat")
    res = api.FileRead(cgmemproc)
    reslist=res.replace("\n"," ").split(" ")
    statdict = dict([(x, y) for x, y in zip(reslist[::2], reslist[1::2])])
    for pagetype in pagetype_list:
        print("%--15s:%--15d k"%(pagetype, int(statdict[pagetype])/4096))
    for pagetype in memtype_list:
        print("%--15s:%--15d k"%(pagetype, int(statdict[pagetype])/4096))

CgMemroydFuncDict={
"stat": CgMemStat,
}

mecommanddict={
"memory":CgMemroydFuncDict,
}

mejsonfile={
"command":mecommanddict,
}

def RunCommandWithFunc(name, cmddict):
    name=name.replace(" ","")
    name=name.split("+")
    for item in name:
        ret=cmddict[item]
        if ret != 0:
            return

def RunCommandWithDict(name, cmddict, FuncDictKey):
    name=name.replace(" ","")
    name=name.split("+")
    for item in name:
        ret=cmddict[item][FuncDictKey]()
        if ret != 0:
            return

def ListCommand():
    for key in mejsonfile["command"]:
        print(("%s  %--20s%--30s")%("command:", key, mejsonfile["command"][key]))

if options.list:
    ListCommand()

if options.run:
    RunCommandWithDict(options.run, mecommanddict,  options.sub)

