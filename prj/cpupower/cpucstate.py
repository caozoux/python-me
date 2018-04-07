#!/usr/bin/python2.7

import os
import re
import time
import random
from optparse import OptionParser
from multiprocessing import cpu_count

def read_sysfs(sysfs_file):
    """read sysfs value
    """
    if os.path.exists(sysfs_file):
        fd=open(sysfs_file, "r")
        val=fd.read()
        fd.close()
        return val
    return ""

def write_sysfs(sysfs_file, str_v):
    """read sysfs value
    """
    if os.path.exists(sysfs_file):
        fd=open(sysfs_file, "w")
        fd.write(str_v)
        fd.close()

def get_cpuidle_sysfs(cpuid):
    """get the cpuid idle sysfs path
    """
    cpuid_sysfs="/sys/devices/system/cpu/cpu?/cpuidle"
    cpuid_sysfs=cpuid_sysfs.replace("?", str(cpuid))
    if os.path.exists(cpuid_sysfs):
        return cpuid_sysfs

    return ""

def get_cpuid_cstate_ctrl_sysf_diction(cpuid):
    """return the cstate control sysfs diction
    """
    ctrl_dic={}

    cpuid_sysfs=get_cpuidle_sysfs(cpuid)
    if not cpuid_sysfs:
        return ""

    for name in os.listdir(cpuid_sysfs):

        #state0 is poll state, we not need it
        if name == "state0":
            continue
        cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
        cpuid_cstate_name_sysfs=os.path.join(cpuid_cstate_sysfs, "name")
        cpuid_cstate_name_str=open(cpuid_cstate_name_sysfs, "r").read()

        res=re.search("C.*-", cpuid_cstate_name_str)
        if res:
            cstate_str=res.group(0)[:-1]
            ctrl_dic[cstate_str]=cpuid_cstate_sysfs

    return ctrl_dic


def get_cpuid_cstate_sysfs(cpuid, cstate):
    """get the cpu cstate sysfs dir
       for exmaple: CPU0-C1
       it is /sys/devices/system/cpu/cpu0/cpuidle/state2"
    """
    diction=get_cpuid_cstate_ctrl_sysf_diction(cpuid)

    if cstate.find("C6") >= 0:
        for cstate_name in diction.keys():
            if cstate_name.find("C6") >= 0:
                return diction[cstate_name]
    else:
        if diction and diction.has_key(cstate):
            return diction[cstate]
    return ""

def read_cstate_sysfs(cpuid, cstate, name):
    """read the /sys/devices/system/cpu/cpu?/cpuidle/name
    """

    cpuid_cstate_sysfs=get_cpuid_cstate_sysfs(cpuid, cstate)
    if cpuid_cstate_sysfs:
        cpuid_cstate_name_sysfs=os.path.join(cpuid_cstate_sysfs, name)
        if os.path.exists(cpuid_cstate_name_sysfs):
            return read_sysfs(cpuid_cstate_name_sysfs)

    return ""

def enable_cpuid_cstate(cpuid_cstate_sysfs, enable):
    """set the cpu cstate disable value
       cpuid_cstate_dis_sysfs: such as /sys/devices/system/cpu/cpu0/cpuidle
       val: 1 disbale cstate, 0 enable cstate
    """
    cpuid_cstate_dis_sysfs=os.path.join(cpuid_cstate_sysfs, "disable")

    if enable:
        write_sysfs(cpuid_cstate_dis_sysfs, "0")
    else:
        write_sysfs(cpuid_cstate_dis_sysfs, "1")

    #check the operation is complete
    val=read_sysfs(cpuid_cstate_dis_sysfs)

    if enable and val[0] != "0":
        print("WARNING:",cpuid_str,cstate," enable failed")
        return 0
    elif not enable and val[0] != "1":
        print("WARNING:",cpuid_str,cstate," disable failed")
        return 0

    return 1

def cstate_control(cpuid, cstate, enable, show=1):
    """control the cpuid cstate en/dis.
       cpuid: cpu id
       cstate: cpu cstate "c1 c2 c3 c4 c5 c6
       enable: en 1, dis 0
       return: success is 1, fail is 0
    """

    cpuid_cstate_sysfs=get_cpuid_cstate_sysfs(cpuid, cstate)
    if not cpuid_cstate_sysfs:
        print("ERROR: not find cpu cstate: %s"%cstate)
        return 1

    if not enable_cpuid_cstate(cpuid_cstate_sysfs, enable):
        return 1;

    if show:
        if enable:
            print("CPU%-3d enable  %s"%(cpuid,cstate))
        else:
            print("CPU%-3d disable %s"%(cpuid,cstate))

    return 0

def cstate_control_mask(cpumask, cstate, enable):
    """control the cpumask cstate en/dis.
       cpumask: cpumaksvalue
       cstate: cpu cstate "c1 c2 c3 c4 c5 c6
       enable: en 1, dis 0
       return: success is 1, fail is 0
    """

    for cpuid in range(128):
        if cpumask & (1<<cpuid):
            if cstate_control(cpuid, cstate, enable, 0):
                print("ERROR: CPU"+str(cpuid)+" cstate control fail")
                return 1
            else:
                print "CPU"+str(cpuid)+" ",

    if enable:
        print("enable "+cstate)
    else:
        print("disable "+cstate)

    return 0

def dump_cpustate_info(cpuid):
    """print the cpuid cstate infomations
       cpuid: cpu id
    """
    cpuid_sysfs=get_cpuidle_sysfs(cpuid)
    cpuid_str="cpu"+str(cpuid)
    cpuid_cstate_list={'name':'', 'disable':'', 'time':'', 'usage':''}

    if not os.path.exists(cpuid_sysfs):
        print("ERROR: not find ",cpuid_str," interface")
        return 1

    #print("%-20s %-20s %-20s %-20s"%(cpuid_str.upper(), "disable", "time", "usage"))
    #for name in os.listdir(cpuid_sysfs):
    #    cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
    #    for item in cpuid_cstate_list:
    #        fs=os.path.join(cpuid_cstate_sysfs, item)
    #        print "%-20s"%(open(fs).read()[:-1]), 
    #    print ""
    print "%-6d "%cpuid,
    for name in os.listdir(cpuid_sysfs):
        cstate_en_str=""
        #state0 is poll state, we not need it
        if name == "state0":
            continue

        cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
        for key in cpuid_cstate_list.keys():
            cpuid_cstate_list[key]=read_sysfs(os.path.join(cpuid_cstate_sysfs, key))[:-1]
        if cpuid_cstate_list['disable'] == "0":
            cstate_en_str="E"
        else:
            cstate_en_str="D"

        print "%7s(%s/%s/%s)"%(cpuid_cstate_list['name'], cstate_en_str, cpuid_cstate_list['time'],cpuid_cstate_list['usage']),
    print ""


def test_c6_cstate(cpu_nums, enable):
    """test all cpu cstate c6 control
       enable: 1 - C6 enable, 0 - C6 disable  
    """

    cputime_old_dic={}
    cputime_dic={}
    rang_max=(1<<cpu_nums)-1;
    rand_val=random.randint(0, rang_max)
    print "TEST: ",



    if enable:
        #enable all mask cpu C6
        ret=cstate_control_mask(rand_val, "C6", 1)
    else:
        #disable all mask cpu C6
        ret=cstate_control_mask(rand_val, "C6", 0)

    if ret:
        print("ERROR: cstate control failed")
        return 1

    time.sleep(1)

    #update time to cputime_old_dic
    for cpuid in range(cpu_nums):
        if rand_val & (1<<cpuid):
            cpuid_str=str(cpuid)
            cputime_old_dic[cpuid_str]=read_cstate_sysfs(cpuid, "C6", "time")
            if  not cputime_old_dic[cpuid_str]:
                print("ERROR: read CPU"+str(cpuid)+" csate time failed")
                return 0

    time.sleep(2)
    #update time to cputime_dic
    for cpuid in range(cpu_nums):
        if rand_val & (1<<cpuid):
            cpuid_str=str(cpuid)
            cputime_dic[cpuid_str]=read_cstate_sysfs(cpuid, "C6", "time")
            if  not cputime_dic[cpuid_str]:
                print("ERROR: read CPU"+str(cpuid)+" csate time failed")
                return 0

    #compare the value between cputime_old_dic and cputime_dic
    for key in cputime_old_dic.keys():
        if cputime_old_dic.has_key(key) \
             and  cputime_dic.has_key(key):
                 if enable:
                     if cputime_old_dic[key] == cputime_dic[key]:
                         retry_cnt=3
                         while retry_cnt>0:
                             time.sleep(1)
                             print("WARNING CPU%s: C6 time is not update in 1s, test it again"%key)
                             cputime_dic[key]=read_cstate_sysfs(int(key), "C6", "time")
                             if cputime_old_dic[key] == cputime_dic[key]:
                                print("WARNGING CPU%-6s cstate enable test failed dealy %ds: %s %s"%\
                                        (key, 3-retry_cnt, cputime_old_dic[key][:-1],cputime_dic[key][:-1]))
                             else:
                                print("WARNING CPU%-6s cstate enable test dealy %ds: %s %s"%\
                                        (key,3-retry_cnt, cputime_old_dic[key][:-1],cputime_dic[key][:-1]))
                                break
                             retry_cnt -= 1
                         if retry_cnt == 0:
                            print("ERROR CPU%-6s cstate enable test failed in 3s: %s %s"%\
                                    (key,cputime_old_dic[key][:-1],cputime_dic[key][:-1]))
                     else:
                         print("INFO CPU%-6s cstate enable test successfully"%key)
                 else:
                     if cputime_old_dic[key] != cputime_dic[key]:
                         print("ERROR CPU%-6s cstate disable test failed"%key)
                         break;
                     else:
                         print("INFO CPU%-6s cstate disable test successfully"%key)

    if enable:
        pass
    else:
        cstate_control_mask(rand_val, "C6", 1)


parser = OptionParser()
parser.add_option("-d", "--disable", action="store",type="string", default="", dest="dis_cpuid",
                  help="-d cpuid -c cstate, disbale cpu cstate", metavar="DERECTORY")

parser.add_option("-e", "--enable",
                  action="store", type="string", dest="en_cpuid", default="",
                  help="-e cpuid -c cstate, enable cpu cstate", metavar="DERECTORY"
                  )

parser.add_option("-c", "--cstate",
                  action="store", type="string", dest="cstate", default="",
                  help="-c cstate, cpu cstate", metavar="DERECTORY"
                  )

parser.add_option("-i", "--info",
                  action="store_true",  dest="info",
                  help="-i show all cpu cstate information",
                  )

parser.add_option("-t", "--test",
                  action="store_true",  dest="test",
                  help="-t run the cycle cstate test",
                  )

parser.add_option("-s", "--show",
                  action="store_true",  dest="cstate_show",
                  help="-s show machine support all cstate"
                  )
(options, args) = parser.parse_args()

if options.info:
    print "CPU      Cstate(enable/time/usage)"
    for cpuid in range(cpu_count()):
        dump_cpustate_info(cpuid)
    exit()


if options.test:
    cpu_cnt=cpu_count()
    while 1:
        if test_c6_cstate(cpu_cnt, 1):
            break

        if test_c6_cstate(cpu_cnt, 0):
            break
    exit()

if options.dis_cpuid:
    cpu_cnt=cpu_count()
    cpuid=int(options.dis_cpuid)
    if cpuid >= cpu_cnt:
        print "ERROR: CPU%s is not found"%options.dis_cpuid
        exit()

    if not options.cstate:
        print "ERROR: CPU%s cstate is miss"%options.dis_cpuid

    cstate_control(cpuid, options.cstate, 0)

if options.en_cpuid:
    cpu_cnt=cpu_count()
    cpuid=int(options.en_cpuid)
    if cpuid >= cpu_cnt:
        print "ERROR: CPU%s is not found"%options.dis_cpuid
        exit()

    if not options.cstate:
        print "ERROR: CPU%s cstate is miss"%options.dis_cpuid

    cstate_control(cpuid, options.cstate, 1)

if options.cstate_show:
    cpu_cnt=cpu_count()
    for cpuid in range(cpu_cnt):
        cpuid_sysfs=get_cpuidle_sysfs(cpuid)
        if not os.path.exists(cpuid_sysfs):
            print("ERROR: not find ",cpuid_str," interface")
            exit()

        print "CPU cstate:",
        for name in os.listdir(cpuid_sysfs):
            #state0 is poll state, we not need it
            if name == "state0":
                continue
            cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
            cpuid_cstate_name_sysfs=os.path.join(cpuid_cstate_sysfs, "name")
            print "%s"%read_sysfs(cpuid_cstate_name_sysfs)[:-1],
        break

