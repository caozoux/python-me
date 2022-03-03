import os
import re
import json
import subprocess
import random
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run run perf script")
parser.add_option("-t", "--time", type="string", dest="time",
                  help="--time perf with -a sleep time")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-o", "--type", type="string", dest="type",
                  help="--type stat_event")
parser.add_option("-s", "--sleep", type="string", dest="sleep",
                  help="--sleep  -a sleep")
parser.add_option("", "--extra_kprobe_function", type="string", dest="extra_kprobe_function",
                  help="--extra_kprobe_function  specficy function name")
parser.add_option("", "--extra_kprobe_function_param", type="string", dest="extra_kprobe_function_param",
                  help="--extra_kprobe_function_param  param like :dfd=%ax filename=%dx flags=%cx mode=+4($stack)")
parser.add_option("", "--extra_kprobe_stacktrace", type="string", dest="extra_kprobe_stacktrace",
                  help="--extra_kprobe_stacktrace           enable kprobe stacktrace")
parser.add_option("-c", "--case", type="string", dest="case",
                  help="--case perf summary dit command")
(options, args) = parser.parse_args()

perfstatrun={
"kvm":"perf -e \"kvm:*\"",
}

perfkprobepre={
"entry":"echo 'p:args0 args1 args2' > /sys/kernel/debug/tracing/kprobe_events",
"ret":  "echo 'r:args0 ret=$retval' > /sys/kernel/debug/tracing/kprobe_events",
}

perfkproberun={
"entry":"echo 1 > /sys/kernel/debug/tracing/events/kprobes/args0/enable",
}

perfkprobeclean={
"entry":"echo 0 > /sys/kernel/debug/tracing/events/kprobes/args0/enable",
}

def PerfStatRun(case):
    print("PerfStatRun")
    pass

def PerfKprobeRun(case):
    if not options.extra_kprobe_function:
        print("Err: kprobe function name not specify")
        return -1;
    precmd=perfkprobepre[case]
    eventname="mykprobe"+ str(random.randint(1,1000))
    precmd=re.sub("args0", eventname, precmd)
    precmd=re.sub("args1", options.extra_kprobe_function, precmd)
    if options.extra_kprobe_function_param:
        precmd=re.sub("args2", options.extra_kprobe_function, precmd)
    else:
        precmd=re.sub("args2", "", precmd)

    if options.extra_kprobe_stacktrace:
        cmdstacktrace="echo 1 > /sys/kernel/debug/tracing/options/stacktrace"
    cmdrun=perfkproberun[case]
    cmdrun=re.sub("args0", eventname, cmdrun)

    cmdclean=perfkprobeclean[case]
    cmdclean=re.sub("args0", eventname, cmdclean)

    print("PerfKprobeRun",precmd, cmdrun, cmdclean)
    if options.extra_kprobe_stacktrace:
        cmdstacktrace="echo 0 > /sys/kernel/debug/tracing/options/stacktrace"
    pass

perfrun={
"stat":PerfStatRun,
"kprobe":PerfKprobeRun,
}

perflist={
"stat":perfstatrun,
"kprobe":perfkproberun,
}


def PerfEventJson(res):
    perfjson = {"type": "", "name": "", "data": ""}
    perfkeymap={}
    lines=res.decode()
    res=re.sub(' +', ' ', lines).strip()
    res=re.sub('\n +', '\n', res).strip()
    newlines=res.split("\n")
    dist=[]
    for line in newlines[2:-2]:
        item=line.split(" ")
        perfkeymap[item[1]]=int(item[0])
    perfjson['type']="perf-kvm"
    perfjson['name']="perf-kvm-2012"
    perfjson['data']=[perfkeymap]
    test=json.dumps(perfjson, ensure_ascii=False,indent=2)
    print(test)


def PerfExecuteCommand(cmd):
    return api.excuteCommand(cmd, 1, 1)

if options.list:
    for key in perflist:
        for item in perflist[key]:
            print(key,": ", perflist[key][item])
if options.type:
    if options.type == "stat":
        PerfExecuteCommand(cmd, )

if options.run and options.case:
    if options.run in perflist and options.case in perflist[options.run]:
        perfrun[options.run](options.case)

