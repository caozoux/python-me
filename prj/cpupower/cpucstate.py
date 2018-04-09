#!/usr/bin/python2.7

import os
import re
import time
import random
from optparse import OptionParser
from multiprocessing import cpu_count
from multiprocessing import Process
import csctrl

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

def process_run():
    """test process run
    """
    cnt=0
    while 1:
        cnt += 1

def read_cpufreq_sysfs(cpuid):
    """read cpuid freq
    """
    cpu_freq_sysfs="/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    cpuid_freq_sysfs=cpu_freq_sysfs.replace("?", str(cpuid))
    if not os.path.exists(cpuid_freq_sysfs):
        print "ERROR: not find cpu freq sys interface"
        return ""

    return read_sysfs(cpuid_freq_sysfs)[:-1]

def get_machine_cstate_list():
    """return the machine support cstate list
    """
    cpuid_cstate_list=[]
    cpu_cnt=cpu_count()
    for cpuid in range(cpu_cnt):
        cpuid_sysfs=csctrl._get_cpuidle_sysfs(cpuid)
        if not os.path.exists(cpuid_sysfs):
            print("ERROR: not find ",cpuid_str," interface")
            exit()

        for name in os.listdir(cpuid_sysfs):
            #state0 is poll state, we not need it
            if name == "state0":
                continue
            cpuid_cstate_sysfs=os.path.join(cpuid_sysfs, name)
            cpuid_cstate_name_sysfs=os.path.join(cpuid_cstate_sysfs, "name")
        break

def dump_cpustate_info(cpuid):
    """print the cpuid cstate infomations
       cpuid: cpu id
    """
    cpuid_sysfs=csctrl._get_cpuidle_sysfs(cpuid)
    cpuid_str="cpu"+str(cpuid)
    cpuid_cstate_list={'name':'', 'disable':'', 'time':'', 'usage':''}

    if not os.path.exists(cpuid_sysfs):
        print("ERROR: not find ",cpuid_str," interface")
        return 1

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

def test_turbost(cpuid):
    """test signal cpu turbost
    """
    cpu_freq_sysfs="/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    cpuid_freq_sysfs=cpu_freq_sysfs.replace("?", str(cpuid))

    if not os.path.exists(cpuid_freq_sysfs):
        print "ERROR: not find cpu freq sys interface"
        return 1

    cpu_cnt=cpu_count()
    ret=csctrl.cstate_control_mask((1<<cpu_cnt)-1, "C6", 1)
    if ret:
        print("ERROR: cstate control failed")
        return 1

    cpu_process=Process(target=process_run)
    cpu_process.start()
    if os.system("taskset -cp "+str(cpuid)+" "+str(cpu_process.pid)+" >& /dev/null"):
        print "ERROR: taskset bind to CPU"+str(cpuid)+" failed"
        os.system("kill -p "+bc_id)

    #poll cpu freq
    poll_time=5
    while poll_time>0:
        print "CPU"+str(cpuid)+" freq: "+read_sysfs(cpuid_freq_sysfs)[:-1]
        time.sleep(1)
        poll_time -= 1

    cpu_process.terminate()

def test_c6_cstate(cpu_nums, enable):
    """test all cpu cstate c6 control
       enable: 1 - C6 enable, 0 - C6 disable
    """

    cputime_old_dic={}
    cputime_dic={}
    rang_max=(1<<cpu_nums)-1;
    rand_val=random.randint(0, rang_max)
    print "TEST:",

    cpu0_dic=csctrl.get_cpuid_cstate_ctrl_sysf_diction(0)
    if cpu0_dic.has_key("C7"):
        if csctrl.cstate_control_mask(rand_val, "C7", 0):
            print "ERROR: disable all cpu C7 failed"
            return 1

    #check C7, if it is exist, disable it
    if enable:
        #enable all mask cpu C6
        ret=csctrl.cstate_control_mask(rand_val, "C6", 1)
    else:
        #disable all mask cpu C6
        ret=csctrl.cstate_control_mask(rand_val, "C6", 0)

    if ret:
        print("ERROR: cstate control failed")
        return 1

    time.sleep(5)

    #update time to cputime_old_dic
    for cpuid in range(cpu_nums):
        if rand_val & (1<<cpuid):
            cpuid_str=str(cpuid)
            cputime_old_dic[cpuid_str]=csctrl._read_cstate_sysfs(cpuid, "C6", "time")
            if  not cputime_old_dic[cpuid_str]:
                print("ERROR: read CPU"+str(cpuid)+" csate time failed")
                return 0

    time.sleep(5)
    #update time to cputime_dic
    for cpuid in range(cpu_nums):
        if rand_val & (1<<cpuid):
            cpuid_str=str(cpuid)
            cputime_dic[cpuid_str]=csctrl._read_cstate_sysfs(cpuid, "C6", "time")
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
                             cputime_dic[key]=csctrl._read_cstate_sysfs(int(key), "C6", "time")
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
                         print("INFO CPU%-6s cstate enable test successfully:%d  freq:%s"%(key, \
                                  int(cputime_dic[key][:-1])- int(cputime_old_dic[key][:-1]), read_cpufreq_sysfs(int(key))))
                 else:
                     if cputime_old_dic[key] != cputime_dic[key]:
                         print("ERROR CPU%-6s cstate disable test failed"%key)
                         break;
                     else:
                         print("INFO CPU%-6s cstate disable test successfully"%key)


    if enable:
        turbost_max=3
        cpu_run_cnt=0
        process_list=[]
        for cnt in range(turbost_max):
            cpu_process=Process(target=process_run)
            process_list.append(cpu_process)

        # test turbost cpu freq
        for cpuid in range(cpu_nums):
            if rand_val & (1<<cpuid):
                cpu_process=process_list[cpu_run_cnt]
                cpu_process.start()
                print "INFO CPU%-3d %6s turbost test"%(cpuid, "run")

                if os.system("taskset -cp "+str(cpuid)+" "+str(cpu_process.pid)+ " >& /dev/null"):
                    print "ERROR: taskset bind to CPU"+str(cpuid)+" failed"
                    return 0
                cpu_run_cnt += 1
                if cpu_run_cnt == turbost_max:
                    break;

        cpu_run_cnt=0
        time.sleep(3)
        for cpuid in range(cpu_nums):
            if rand_val & (1<<cpuid):
                print  "INFO CPU%-3d %10s cpufreq:%s"%(cpuid, "turbost", read_cpufreq_sysfs(cpuid))
                cpu_run_cnt += 1
                if cpu_run_cnt == turbost_max:
                    break;

        # exit cpu run process
        for process in process_list:
            process.terminate()
    else:
        csctrl.cstate_control_mask(rand_val, "C6", 1)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--disable", action="store",type="string", default="", dest="dis_cpuid",
                      help="-d cpuid -c cstate, disbale cpu cstate", metavar="cpuid")

    parser.add_option("-e", "--enable",
                      action="store", type="string", dest="en_cpuid", default="",
                      help="-e cpuid -c cstate, enable cpu cstate", metavar="cpuid"
                      )

    parser.add_option("-c", "--cstate",
                      action="store", type="string", dest="cstate", default="",
                      help="-c cstate, cpu cstate", metavar="cstate such as \"C6\""
                      )

    parser.add_option("-i", "--info",
                      action="store_true",  dest="info",
                      help="-i show all cpu cstate information",
                      )

    parser.add_option("-t", "--test",
                      action="store_true",  dest="test",
                      help="-t run the cycle cstate test",
                      )

    parser.add_option("-b", "--turbost",
                      action="store", type="string", dest="turbost", default="",
                      help="-b cpuid , run turbost test for cpuid",
                      )

    parser.add_option("-s", "--show",
                      action="store_true",  dest="cstate_show",
                      help="-s show machine support all cstate"
                      )
    (options, args) = parser.parse_args()

    if not os.getenv("SUDO_USER"):
        print "ERROR: sudo access is need"
        exit()

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

    if options.turbost:
        cpu_cnt=cpu_count()
        cpuid=int(options.turbost)
        if cpuid >= cpu_cnt:
            print "ERROR: CPU%s is not found"%options.dis_cpuid
            exit()
        test_turbost(int(cpuid))
        exit()

    if options.dis_cpuid:
        cpu_cnt=cpu_count()
        cpuid=int(options.dis_cpuid)
        if cpuid >= cpu_cnt:
            print "ERROR: CPU%s is not found"%options.dis_cpuid
            exit()

        if not options.cstate:
            print "ERROR: CPU%s cstate is miss"%options.dis_cpuid

        csctrl.cpu_cstate_control(cpuid, options.cstate, -1)

    if options.en_cpuid:
        cpu_cnt=cpu_count()
        cpuid=int(options.en_cpuid)
        if cpuid >= cpu_cnt:
            print "ERROR: CPU%s is not found"%options.dis_cpuid
            exit()

        if not options.cstate:
            print "ERROR: CPU%s cstate is miss"%options.dis_cpuid

        csctrl.cpu_cstate_control(cpuid, options.cstate, 1)

    if options.cstate_show:
        cpu_cnt=cpu_count()
        for cpuid in range(cpu_cnt):
            cpuid_sysfs=csctrl._get_cpuidle_sysfs(cpuid)
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

