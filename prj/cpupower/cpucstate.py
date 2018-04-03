#!/usr/bin/python2.7

import os
import re
import time
import random

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
    dis_fd=open(cpuid_cstate_dis_sysfs, "w")
    if enable:
        dis_fd.write("0")
    else:
        dis_fd.write("1")
    dis_fd.close()

    #check the operation is complete
    dis_fd=open(cpuid_cstate_dis_sysfs, "r")
    val=dis_fd.read()
    dis_fd.close()

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
    cpuid_cstate_list=["name", "disable", "time", "usage"]

    if not os.path.exists(cpuid_sysfs):
        print("ERROR: not find ",cpuid_str," interface")
        return 1

    print("%-20s %-20s %-20s %-20s"%(cpuid_str.upper(), "disable", "time", "usage"))
    for name in os.listdir(cpuid_sysfs):
        cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
        for item in cpuid_cstate_list:
            fs=os.path.join(cpuid_cstate_sysfs, item)
            print "%-20s"%(open(fs).read()[:-1]), 
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


#cstate_control_mask(0xffffff, "C7", 0)
#cstate_control(0, "C6", 0)
#dump_cpustate_info(0)
#print get_cpuid_cstate_ctrl_sysf_diction(0)
#test_signal_cpu_c6(0)
while 1:
    if test_c6_cstate(96, 1):
        break
	
    if test_c6_cstate(96, 0):
        break

