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




