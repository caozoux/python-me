#!/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import signal

from time import sleep
from collections import defaultdict
from optparse import OptionParser

G_FTRACE_DIR="/sys/kernel/debug/tracing/"

parser = OptionParser()
parser.add_option("-s", "--stacktrace", type="string", dest="stacktrace",
                  help="--stacktrace get kernel function stacktrace dump")
parser.add_option("-p", "--pid", type="string", dest="pid",
                  help="--pid  specify proccessor pid")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all") 
(options, args) = parser.parse_args()

#dumpstack = defaultdict(lambda: defaultdict(int))
dumpstack = defaultdict(int)

def _signal_ignore(signal, frame):
    print()

def dump_trace():
    lines=open("/sys/kernel/debug/tracing/trace", 'r').readlines()
    i = 0
    while i < len(lines):
        if "stack trace" in lines[i]:
            stackdump=[]
            i += 1
            #print(lines[i])
            while i < len(lines):
                if not lines[i][:4] == " => ":
                    #print(stackdump, lines[i][:2])
                    last=stackdump[len(stackdump)-1]
                    stackdump[len(stackdump)-1] = last[:-1]
                    dumpstack["".join(stackdump)] += 1
                    #print(stackdump, "".join(stackdump))
                    #exit(0)
                    break;
                stackdump.append(lines[i][4:])
                i += 1
        i += 1
    for key in dumpstack:
        print(key)
        print("count:", dumpstack[key],"\n")

def dump_start():
    os.system("echo nop > /sys/kernel/debug/tracing/current_tracer")
    os.system("echo \"\" > /sys/kernel/debug/tracing/trace")
    os.system("echo function > /sys/kernel/debug/tracing/current_tracer")
    os.system("echo 1 > /sys/kernel/debug/tracing/options/func_stack_trace")
    os.system("echo "+options.stacktrace+" > /sys/kernel/debug/tracing/set_ftrace_filter")
    os.system("echo 1 > /sys/kernel/debug/tracing/tracing_on")

def dump_stop():
    os.system("echo 0 > /sys/kernel/debug/tracing/tracing_on")

def run_stacktrace():
    exiting =0
    #traceing_on= os.path.join(G_FTRACE_DIR, "traceing_on")
    dump_start()
    while True:
        if exiting:
            exit(0)

        try:
            sleep(10)
        except KeyboardInterrupt:
            print("zz")
            dump_stop()
            dump_trace()
            signal.signal(signal.SIGINT, _signal_ignore)
            exiting = 1;

runfunc=""
if options.stacktrace:
    runfunc=run_stacktrace

try:
    runfunc()
except Exception:
    if sys.exc_info()[0] is not SystemExit:
        print(sys.exc_info()[1])

