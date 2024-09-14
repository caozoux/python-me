#!/bin/python3

import os
import time
from optparse import OptionParser;

monitor_mode=["total", "sys", "ksoftirq", "hwirq"]
monitor_throshod=0
monitor_period=10
monitor_verbose=0

cpustat_total=[]
perfcpustat_list=[]
CPU_NUM=-1

CPU_LOAD_TOTAL=[]
OLDCPU_LOAD_TOTAL=[]
PERCPU_LOAD_LIST=[]
OLDPERCPU_LOAD_LIST=[]
KSOFTIRQ_LOAD=[]
OLDKSOFTIRQ_LOAD=[]


from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m", "--mode", action="store", type="string", default="total", dest="mode",
				  help="--mode cpu/sys/ksoftirq/hwirq")

parser.add_option("-t", "--threshod", action="store", type="int", default=0, dest="threshod",
				  help="--threshod the monitor throshold of cpu user_util")
parser.add_option("-p", "--period", action="store", type="int", default=10, dest="period",
				  help="--period monitor period time, default 10s ")
parser.add_option("-f", "--filter", action="store", type="string", default="", dest="filter",
				  help="--filter sys/si/hwirq")
parser.add_option("-v", "--verbose", action="store_true",  default=0, dest="verbose",
				  help="--verbose monitor period time, default 10s ")

(options, args) = parser.parse_args()

if options.threshod:
	monitor_throshod = options.threshod

if options.period:
	monitor_period = options.period

if options.verbose:
	monitor_verbose = options.verbose

if monitor_throshod == 0:
	print("Err: please set monitoring threshod value")
	exit(1)

def dump_cpu_runstat(cpustat):
	total = 0
	user = int(cpustat[0])
	nice = int(cpustat[1])
	system = int(cpustat[2])
	idle = int(cpustat[3])
	iowait= int(cpustat[4])
	irq = int(cpustat[5])
	softirq = int(cpustat[6])
	total = user + nice + system + idle  + irq + softirq

	print("%.1f"%((total-idle)/total*100))
	print(total, user, system, idle)

def get_percpu_load(cpustat):
	total = 0
	user = int(cpustat[0])
	nice = int(cpustat[1])
	system = int(cpustat[2])
	idle = int(cpustat[3])
	iowait= int(cpustat[4])
	irq = int(cpustat[5])
	softirq = int(cpustat[6])
	total = user + nice + system + idle  + irq + softirq
	return total, user, nice, system, idle, iowait, irq, softirq

def get_ksoftirq_diff(new, old):
	"""TODO: Docstring for get_ksoftirq_diff.
	:returns: TODO

	"""
	pass
def get_cpuload_diff(cpustat, old_cpustat):
	total, user, nice, system, idle, iowait, irq, softirq = get_percpu_load(cpustat)
	old_total, old_user, old_nice, old_system, old_idle, old_iowait, old_irq, old_softirq = get_percpu_load(old_cpustat)

	diff_total = total - old_total
	diff_user = user - old_user
	diff_nice = nice - old_nice
	diff_system = system - old_system
	diff_idle = idle - old_idle
	diff_iowait = iowait - old_iowait
	diff_irq = irq - old_irq
	diff_softirq = softirq - old_softirq

	return diff_total, diff_user, diff_nice, diff_system, diff_idle, diff_iowait, diff_irq, diff_softirq

res=open("/proc/stat", 'r').readlines()
#get cpus number
for line in res:
	if line[:3] == "cpu":
		CPU_NUM += 1
	else:
		break

CPU_LOAD_TOTAL=res[0][5:-1].split(" ")
OLDCPU_LOAD_TOTAL=CPU_LOAD_TOTAL
KSOFTIRQ_LOAD=res[11][8:-1].split(" ")
OLDKSOFTIRQ_LOAD=res[11][8:-1].split(" ")

#print(CPU_LOAD_TOTAL)
for i in range(CPU_NUM):
	if len(PERCPU_LOAD_LIST) < i+1:
		PERCPU_LOAD_LIST.append(res[i+1][:-1].split(" ")[1:])
		OLDPERCPU_LOAD_LIST.append(res[i+1][:-1].split(" ")[1:])

time.sleep(1)
res=open("/proc/stat", 'r').readlines()
CPU_LOAD_TOTAL=res[0][5:-1].split(" ")
OLDCPU_LOAD_TOTAL=CPU_LOAD_TOTAL
KSOFTIRQ_LOAD=res[11][8:-1].split(" ")
OLDKSOFTIRQ_LOAD=res[11][8:-1].split(" ")
for i in range(CPU_NUM):
	PERCPU_LOAD_LIST[i]=(res[i+1][:-1].split(" ")[1:])
	OLDPERCPU_LOAD_LIST[i]=PERCPU_LOAD_LIST[i]
time.sleep(1)

while  1 :
	record_cpu=[]
	res=open("/proc/stat", 'r').readlines()
	CPU_LOAD_TOTAL=res[0][:-1].split(" ")[2:]

	diff_total, diff_user, diff_nice, diff_system, diff_idle, diff_iowait, diff_irq, diff_softirq = get_cpuload_diff(CPU_LOAD_TOTAL, OLDCPU_LOAD_TOTAL)
	OLDCPU_LOAD_TOTAL = CPU_LOAD_TOTAL

	if diff_total == 0:
		continue

	if monitor_verbose:
		print("cpu	%-8s %-8s %-8s %-8s %-8s"%("total", "use", "sys", "si", "hi"))

	cpu_user_util   =   (((diff_total-diff_idle)/diff_total)*100)
	user_user_util  =	((diff_user/diff_total)*100)
	sys_user_util   =	((diff_system/diff_total)*100)
	ksoft_user_util =  ((diff_softirq/diff_total)*100)
	hw_user_util	=	 ((diff_irq/diff_total)*100)

	if monitor_verbose:
		print("cpu	%-8.1f %-8.1f %-8.1f %-8.1f %-2.1f"%(cpu_user_util, user_user_util, sys_user_util, ksoft_user_util, hw_user_util))

	for i in range(CPU_NUM):
		PERCPU_LOAD_LIST[i]=(res[i+1][:-1].split(" ")[1:])
		cpustat = PERCPU_LOAD_LIST[i]

		old_cpustat = OLDPERCPU_LOAD_LIST[i]
		OLDPERCPU_LOAD_LIST[i]=PERCPU_LOAD_LIST[i]

		total, user, nice, system, idle, iowait, irq, softirq = get_percpu_load(cpustat)
		old_total, old_user, old_nice, old_system, old_idle, old_iowait, old_irq, old_softirq = get_percpu_load(old_cpustat)

		diff_total, diff_user, diff_nice, diff_system, diff_idle, diff_iowait, diff_irq, diff_softirq = get_cpuload_diff(cpustat, old_cpustat)
		if diff_total == 0:
			continue

		cpu_user_util   =	(((diff_total-diff_idle)/diff_total)*100)
		user_user_util  =   ((diff_user/diff_total)*100)
		sys_user_util   =	((diff_system/diff_total)*100)
		ksoft_user_util =  ((diff_softirq/diff_total)*100)
		hw_user_util	=	 ((diff_irq/diff_total)*100)

		if monitor_verbose:
			print("cpu%-3d %-8.1f %-8.1f %-8.1f %-8.1f %-2.1f"%(i, cpu_user_util, user_user_util, sys_user_util, ksoft_user_util, hw_user_util))
		if sys_user_util >= monitor_throshod:
			record_cpu.append(i)
	if len(record_cpu) > 0:
		perfcpu_args=""
		perfcpu_args = str(record_cpu[0])
		for i in range(1, len(record_cpu)):
			perfcpu_args +=","+str(record_cpu[i])
		print("perf record -C " + perfcpu_args + " -a -g -o  /var/log/kat/persysmonitor.data sleep 10")
		os.system("perf record -C " + perfcpu_args + " -a -g -o  /var/log/kat/persysmonitor.data sleep 10")
		exit(0)
