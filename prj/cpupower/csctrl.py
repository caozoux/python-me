import os
import re
from multiprocessing import cpu_count

def _read_sysfs(sysfs_file):
    """read sysfs value
    """
    if os.path.exists(sysfs_file):
        fd=open(sysfs_file, "r")
        val=fd.read()
        fd.close()
        return val
    return ""

def _write_sysfs(sysfs_file, str_v):
    """read sysfs value
    """
    if os.path.exists(sysfs_file):
        fd=open(sysfs_file, "w")
        fd.write(str_v)
        fd.close()

def _get_cpuidle_sysfs(cpuid):
    """get the cpuid idle sysfs path
    """
    cpuid_sysfs="/sys/devices/system/cpu/cpu?/cpuidle"
    cpuid_sysfs=cpuid_sysfs.replace("?", str(cpuid))
    if os.path.exists(cpuid_sysfs):
        return cpuid_sysfs

    return ""

def _get_cpuid_cstate_sysfs(cpuid, cstate):
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

def _read_cstate_sysfs(cpuid, cstate, name):
    """read the /sys/devices/system/cpu/cpu?/cpuidle/name
    """

    cpuid_cstate_sysfs=_get_cpuid_cstate_sysfs(cpuid, cstate)
    if cpuid_cstate_sysfs:
        cpuid_cstate_name_sysfs=os.path.join(cpuid_cstate_sysfs, name)
        if os.path.exists(cpuid_cstate_name_sysfs):
            return _read_sysfs(cpuid_cstate_name_sysfs)

    return ""

def get_cpuid_cstate_ctrl_sysf_diction(cpuid):
    """return the cstate control sysfs diction
    """
    ctrl_dic={}

    cpuid_sysfs=_get_cpuidle_sysfs(cpuid)
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

def enable_cpuid_cstate(cpuid_cstate_sysfs, enable):
    """set the cpu cstate disable value
       cpuid_cstate_dis_sysfs: such as /sys/devices/system/cpu/cpu0/cpuidle
       val: 1 disbale cstate, 0 enable cstate
    """
    cpuid_cstate_dis_sysfs=os.path.join(cpuid_cstate_sysfs, "disable")

    if enable:
        _write_sysfs(cpuid_cstate_dis_sysfs, "0")
    else:
        _write_sysfs(cpuid_cstate_dis_sysfs, "1")

    #check the operation is complete
    val=_read_sysfs(cpuid_cstate_dis_sysfs)

    if enable and val[0] != "0":
        print("WARNING:",cpuid_str,cstate," enable failed")
        return 0
    elif not enable and val[0] != "1":
        print("WARNING:",cpuid_str,cstate," disable failed")
        return 0

    return 1

def cstate_control_mask(cpumask, cstate, enable):
    """control the cpumask cstate en/dis.
       cpumask: cpumaksvalue
       cstate: cpu cstate "c1 c2 c3 c4 c5 c6
       enable: en 1, dis 0
       return: success is 1, fail is 0
    """

    for cpuid in range(128):
        if cpumask & (1<<cpuid):
            if cpu_cstate_control(cpuid, cstate, enable, 0):
                print("ERROR: CPU"+str(cpuid)+" cstate control fail")
                return 1
            else:
                print "CPU"+str(cpuid)+" ",

    if enable:
        print("enable "+cstate)
    else:
        print("disable "+cstate)

    return 0

def cpu_cstate_control(cpuid, cstate, enable, show=1):
    """control the cpuid cstate en/dis.
       cpuid: cpu id
       cstate: cpu cstate "c1 c2 c3 c4 c5 c6
       enable: en 1, dis 0
       return: success is 1, fail is 0
    """

    cpuid_cstate_sysfs=_get_cpuid_cstate_sysfs(cpuid, cstate)
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

def scoket_cstate_control(socketid, cstate, enable, show=1):
    """control the socketid cstate en/dis.
       socketid: cpu socketid
       cstate: cpu cstate "c1 c2 c3 c4 c5 c6
       enable: en 1, dis 0
       return: success is 1, fail is 0
    """
    cpu_package_sysfs="/sys/devices/system/cpu/cpu?/topology/physical_package_id"
    cpu_cnt=cpu_count()

    for cpuid in range(cpu_cnt):
        cpuid_package_sysfs=cpu_package_sysfs.replace("?",str(cpuid))
        if not os.path.exists(cpuid_package_sysfs):
            print "WARNING: CPU%-3d %s not find"%(cpuid, cpuid_package_sysfs)
            continue

        package_id=_read_sysfs(cpuid_package_sysfs)[:-1]
        if not package_id:
            print "WARNING: CPU%-3d %s read failed"%(cpuid, cpuid_package_sysfs)
            continue

        if int(package_id) == socketid:
            if not cpu_cstate_control(cpuid, cstate, enable):
                print "ERROR: socket control failed"
                return 1

    print "package%-2d CS:%s enable:%d"%(socketid, cstate, enable)
    return 0

