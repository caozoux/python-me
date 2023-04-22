import os
import re
import time


"""
 /proc/buddyinfo
 /proc/diskstats
 /proc/loadavg
 /proc/meminfo
 /proc/schedstat
 /proc/buddyinfo
 /proc/slabinfo
 /proc/softirqs
 /proc/schedstat
 /proc/stat
 /proc/vmstat
 /proc/vmstat
 /proc/zoneinfo
"""

CPU_NUM=0
def proc_format(procfile, context):
    procdict={}
    array=[]
    desarray=[]
    if procfile == "/proc/buddyinfo":
        datades=["node", "4k", "8k", "16k", "32k", "64k", "128k", "256k", "512k", "1M", "2M", "4M"]
        procdict["datades"] = datades
        for line in context:
            item=line.split(" ")
            des=item[3]
            data=item[4:]
            array.append(data)
            desarray.append(des)
        procdict["data"] = array
        procdict["des"] = desarray
        return procdict
    if procfile == "/proc/stat":
        datades =["cpu", "user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice"]
        for line in context:
            linearray=line.strip().split(" ")
            if linearray[0][:3] != "cpu":
                break
            data=linearray[1:]
            des=linearray[0]
            array.append(data)
            desarray.append(des)
        procdict["datades"] = datades
        procdict["data"] = array
        procdict["des"] = desarray
        return procdict
    if procfile == "/proc/diskstats":
        datades=["disk", "r_io", "r_merge", "r_sector", "r_time" ,"w_io", "w_merge", "w_sector", "w_time", "inflight", "io_tick", "t_queue", "w_time","d_io", "d_merge", "d_sector", "d_time","unkown", "unkown", "unkown", "unkown"]
        procdict["datades"] = datades
        for line in context:
            linearray=line.strip().split(" ")
            data=linearray[3:]
            des=linearray[2]
            array.append(data)
            desarray.append(des)

        procdict["datades"] = datades
        procdict["data"] = array
        procdict["des"] = desarray
        #print(desarray)
        #print(datades)
        #print(array)
        #exit(1)
        return procdict
    if procfile == "/proc/vmstat":

        exit(1)

def proc_array(procfile):
    resarray=[]
    res = open(procfile, 'r').readlines()
    for item in res:
        linearray=re.sub(" +"," ",item[:-1].strip(" "))
        resarray.append(linearray)

    return resarray

def proc_vmstat_diff():
    array_old=proc_array("/proc/vmstat")
    time.sleep(1)
    array_new=proc_array("/proc/vmstat")
    for i in range(len(array_old)):
        old = array_old[i]
        new = array_new[i]
        if old != new:
            item_old=old.split(" ")
            item_new=new.split(" ")
            print("%-15s %d"%(item_old[0], int(item_new[1]) - int(item_old[1])))
def proc_dump(procfile):
    array=proc_array(procfile )
    procdict=proc_format(procfile, array)
    des=procdict["des"]
    data=procdict["data"]
    datades=procdict["datades"]
    #try:
    #except Exception as e:
    #    return 

    for item in datades:
        print("%-10s"%item, end="")
    print()
    for i in range(len(data)):
        item=data[i]
        print("%-10s"%des[i], end="")
        for iteml1 in item:
            print("%-10s"%iteml1, end="")
        print()

def proc_diff_dump(procfile,inter):
    array_old=proc_array(procfile )
    procdict_old=proc_format(procfile, array_old)
    des=procdict_old["des"]
    datades=procdict_old["datades"]

    data_old=procdict_old["data"]

    time.sleep(inter)

    array_new=proc_array(procfile )
    procdict_new=proc_format(procfile, array_new)
    data_new=procdict_new["data"]

    for item in datades:
        print("%-10s"%item, end="")
    print()

    for i in range(len(data_new)):
        item_new=data_new[i]
        item_old=data_old[i]
        print("%-10s"%des[i], end="")
        for l in range(len(item_new)):
            diff = int(item_new[l]) - int(item_old[l])
            print("%-10s"%diff, end="")
        print()

class ProcMonitor(object):

    """Docstring for ProcMonitor. """

    def __init__(self, procfile):
        """TODO: to be defined. """
        self.mProcfile = procfile

    def dump(self, show=0):
        array=proc_array(self.mProcfile) 
        proc_format(self.mProcfile, array)

class ProcTList(object):

    """title and list to map the /proc/xx """
    def __init__(self, showlist, show=1):
        self.mShowStrList=showlist
        self.mIsShow=show
        self.mDataList=[]
        self.mDataListManage=[]
    def EndAddItem(self):
        self.mDataListManage.append(self.mDataList)
        self.mDataList=[]

    def AddItem(self, tstr, astr, show=1):
        """ add a list item into manage list
            tstr: the first left show string
            astr: the others show string
        """
        self.mDataList.append(re.split(r"[ ]+", astr))

    def Dump(self):
        """print all the ProcTList mShowStrList and mDataList
        """
        lastitem=""
        if len(self.mDataListManage) !=0:
            lastitem=self.mDataListManage[-1]
            #print(lastitem)

        for item in self.mShowStrList:
            print("{:<15}".format(item), end="")
        print("")

        for index_l1 in range(len(self.mDataList)):
            xitem = self.mDataList[index_l1]
            for index in range(len(xitem)):
                if lastitem and index != 0:
                    yitem = lastitem[index_l1]
                    print("{:<15}".format(xitem[index]+"("+str(int(xitem[index])- int(yitem[index]))+")"), end="")
                else:
                    print("{:<15}".format(xitem[index]), end="")

            print("")

class ProcManage(object):

    """Docstring for ProcManage. """

    def __init__(self, filepath):
        """TODO: to be defined. """
        self.oFilePath=filepath
        self.oProcReadBuf=""

        self.mCpuStat=""
        self.mCtxtStat=""
        self.mBtimeStat=""
        self.mProcessStat=""
        self.mProcrStat=""
        self.mProcbStat=""
        self.mSoftirqStat=""

    def initialization(self):
        """read the proc patch and transfer into list
        """
        self.mCpuStat=ProcTList(["user", "nice", "system", "idle", 
                "iowait", "irq", "softirq", "steal", "guest", "guest_nice"])
        self.mCtxtStat=ProcTList(["ctxt"])
        self.mBtimeStat=ProcTList(["btime"])
        self.mProcessStat=ProcTList(["processes"])
        self.mProcrStat=ProcTList(["procs_running"])
        self.mProcbStat=ProcTList(["procs_blocked"])
        self.mSoftirqStat=ProcTList(["name","hi","timer","nettx",
            "netrx","block","irqpoll","tasklet",
            "sched","hrtimer","rcu","total"])

    def decodeProc(self):
        """decode the proc interface into human readable txt
        """
        #decode cpu proc/stat
        fd=os.open(self.oFilePath, os.O_RDONLY)
        buffer=os.read(fd, 16024)
        self.oProcReadBuf=buffer.decode().splitlines()
        for item in self.oProcReadBuf:
            if item[:3] == "cpu":
                self.mCpuStat.AddItem("test", item)
            elif item[:4] == "ctxt":
                self.mCtxtStat.AddItem("ctxt", item)
            elif item[:5] == "btime":
                self.mBtimeStat.AddItem("btime", item)
            elif item[:9] == "processes":
                self.mProcessStat.AddItem("processes", item)
            elif item[:13] == "procs_running":
                self.mProcrStat.AddItem("procs_running", item)
            elif item[:13] == "procs_blocked":
                self.mProcbStat.AddItem("procs_blocked", item)
            elif item[:7] == "softirq":
                self.mSoftirqStat.AddItem("softirq", item)
        self.mCpuStat.Dump()
        os.close(fd)
        self.mCpuStat.EndAddItem()
        self.mCtxtStat.EndAddItem()
        self.mBtimeStat.EndAddItem()
        self.mProcessStat.EndAddItem()
        self.mProcrStat.EndAddItem()
        self.mProcbStat.EndAddItem()
        self.mSoftirqStat.EndAddItem()
        #self.mSoftirqStat.Dump()


if __name__ == "__main__":
    proc_vmstat_diff()
    #array=proc_dump("/proc/diskstats")
    #exit(1)
    while 1:
        print("=============")
        proc_vmstat_diff()
        #array=proc_diff_dump("/proc/diskstats",1)
    mProcManage=ProcManage("/proc/stat")
    mProcManage.initialization()
    mProcManage.decodeProc()
    time.sleep(1)
    mProcManage.decodeProc()
    time.sleep(1)
    mProcManage.decodeProc()

