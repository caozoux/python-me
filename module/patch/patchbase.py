#!/usr/bin/env python2.7
import re
import sys
import os

class PatchBase(object):
    """Docstring for PatchBase. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

    @staticmethod
    def getFilesFromPatch(patchname):
        "get the files from patch. these files are created, del or modified by patch"
        retlist=[]
        filebuf = open(patchname).read()
        off = 0;
        while 1:
            res = re.search("\n\+\+\+ b/.*\n", filebuf[off:])
            if res:
                retline = res.group(0)[7:-1]
                retlist.append(retline)
            else:
                break
            ret = filebuf[off:].find(res.group(0)[1:-1])
            if ret:
                off += ret+1

        if len(retlist) == 0:
            return ""
        return retlist

    @staticmethod
    def transferPatchToBuf(remote, commit):
        "transfer the patch to memory buf"
        return os.popen("git -C "+remote+" show "+commit).read()

    @staticmethod
    def getPatchModifiedItem(patchname, number):
        "get the patch item txt context by the specified number"
        filebuflines = open(patchname).readlines()
        filebuf = open(patchname).read()
        retlist=re.findall("\n\@\@.*\n", filebuf)
        if len(retlist):
            size =len(retlist);
            index = filebuflines.index(retlist[number][1:])
            if index < 0:
                return ""
            if number == (size-1):
                return filebuflines[index:-3]
            else:
                index_end = filebuflines.index(retlist[number+1][1:])
                return filebuflines[index:index_end]

    @staticmethod
    def getPatchModifiedItemByConflictNumber(patchname, conflictnumber, srcfile):
        "get the patch item txt context by the specified number"
        filebuflines = open(patchname).readlines()
        filebuf = open(patchname).read()
        retlist=re.findall("\n\@\@.*\n", filebuf)
        if len(retlist):
            size =len(retlist);
            res=re.search("\n\@\@ -"+str(conflictnumber)+".*\n", filebuf)
            if res:
                number=retlist.index(res.group(0))
            else:
                return ""
            index = filebuflines.index(retlist[number][1:])
            if index < 0:
                return ""
            if number == (size-1):
                return filebuflines[index:-3]
            else:
                index_end = filebuflines.index(retlist[number+1][1:])
                return filebuflines[index:index_end]

    @staticmethod
    def getPatchModifiedFileByItem(patchname, number):
        "get the modified file name by the specified patch item number"
        filebuflines = open(patchname).readlines()
        filebuf = open(patchname).read()
        retlist=re.findall("\n\@\@.*\n", filebuf)
        if len(retlist):
            size =len(retlist);
            patchitem_head=retlist[number][1:]
            index = filebuflines.index(retlist[number][1:])
            retlistfiles=re.findall("\n\+\+\+ b.*\n", "".join(filebuflines[:index]))
            return retlistfiles[-1][7:-1]

class PatchContext(PatchBase):
    """Docstring for PatchContext. """

    def __init__(self, filename):
        """TODO: to be defined1. """
        self.patchName=filename
        self.patchModifiedFiles=[]
        self.patchBuf=""

    def init(self):
        """TODO: Docstring for init.
        """
        self.patchBuf=open(filename).read()
        self.patchModifiedFiles= PatchBase.getFilesFromPatch(self.patchname)

#PatchMergeItem is the merge patch
class PatchMergeItem(object):
    def __init__(self, remote, commit):
        """TODO: to be defined1. """
        self.remote = remote
        self.mergeCommit = commit
        self.buf=""
        self.mergeEndCommit=""
        self.mergeStartCommit=""
        self.init()

    def init(self):
        self.buf = PatchBase.transferPatchToBuf(self.remote, self.mergeCommit)

    def formatMergeBranchPatchesByCommit(self, outdir="./", startnumber=1):
        "format all patches in this branch merge"
        if self.isBranchMerge():
            res = re.search("\*.*\n", self.buf)
            off_2 = self.buf.find(res.group(0))
            line_cnt = self.buf[off_2:].count("\n")
            patchnumber = int(line_cnt)-2
            os.system("git -C "+self.remote+" format-patch -"+str(patchnumber)+" "+self.mergeCommit+" --start-number "+startnumber+" -o "+outdir)

    def formatMergeBranchPatchesByCommit(self, outdir="./", startnumber=1):
        "format all patches in this branch merge"
        if self.isBranchMerge():
            res = re.search("\*.*\n", self.buf)
            off_2 = self.buf.find(res.group(0))
            line_cnt = self.buf[off_2:].count("\n")
            patchnumber = int(line_cnt)-2
            os.system("git -C "+self.remote+" format-patch -"+str(patchnumber)+" "+self.mergeCommit+" --start-number "+startnumber+" -o "+outdir)

    def isBranchMerge(self):
        res = re.search("Merge branch .*\n", self.buf)
        if res:
            print(res.group(0))
            #res = re.search("\n\n", self.buf)
            return 1
        return 0

    def getStartEnd(self):
        """get the patch list with start and end commit from merge patch
        :arg1: TODO
        :returns: TODO

        """
        res = re.search("\tMerge:.*\n", self.buf)
        if res:
            self.mergeStartCommit =  res.group(0)[7:].split(" ")[0]
            self.mergeEndCommit = res.group(0)[7:].split(" ")[1][:-1]
            print(self.mergeStartCommit, self.mergeEndCommit)

if __name__ == "__main__":
    #print PatchBase.getPatchModifiedItem(sys.argv[1], 0)
    #print PatchBase.getPatchModifiedFileByItem(sys.argv[1], 0)
    print(PatchBase.getPatchModifiedItemByConflictNumber(sys.argv[1], 494, ""))
