import os
import re
import time

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
    mProcManage=ProcManage("/proc/stat")
    mProcManage.initialization()
    mProcManage.decodeProc()
    time.sleep(1)
    mProcManage.decodeProc()
    time.sleep(1)
    mProcManage.decodeProc()

