import os
import sys
import re

class ProcIoMemDecode(object):
    def __init__(self):
        self.iomembuf=""
        self.usememory_size=0
        self.resvermemory_size=0

    def showline(self, datalist, exter=0):
       print("{:<13}:".format((datalist[2])), end="")
       print("{:<13}".format((datalist[0])), end="")
       print("{:<13}".format((datalist[1])), end="")
       if datalist[2] == "reserved":
            print(" = 0x{:<15x}".format(int(datalist[1],16) - int(datalist[0], 16) + 1))
       else:
            print(" = 0x{:<15x}".format(int(datalist[1],16) - int(datalist[0], 16) + 1))

    #init /proc/iomem
    def ReadFromIOMEM(self):
        lastoff=0
        self.iomembuf=open("/proc/iomem", "r").readlines()

        for line in self.iomembuf:
            line=line.replace(" ", "").replace("-", " ").replace(":", " ").replace("\n", "")
            datalist=line.split(" ")
            self.showline(datalist)
            # should sub the size from the top level memory range
            if datalist[2] == "reserved" or datalist[2] == "Reserved":
                if lastoff > int(datalist[1],16):
                    self.usememory_size -= int(datalist[1],16) - int(datalist[0], 16) + 1
                self.resvermemory_size += int(datalist[1],16) - int(datalist[0], 16) + 1
            else:
                if datalist[2] == "SystemRAM":
                    if lastoff < int(datalist[1],16):
                        self.usememory_size += int(datalist[1],16) - int(datalist[0], 16) + 1

            if lastoff < int(datalist[1],16):
                lastoff = int(datalist[1],16)

        #print("usememory:     {:<15}".format(self.usememory_size))
        print("usememory:     {:<15}".format(self.usememory_size/1024/1024))
        print("resvermemory:  {:<15}".format(self.resvermemory_size/1024/1024))

O_ProcIomem=ProcIoMemDecode()
O_ProcIomem.ReadFromIOMEM()

