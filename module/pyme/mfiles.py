#!/usr/bin/env python2.7
import os
import getopt
import re


class fileDirList:
    filelist = []
    def __init__(self, dir):
        self.filelist= os.popen("ls "+dir).readlines();

    def getFileName(index):
        return filelist[index];

    def rmFileName(index):
        filelist.remove(index)


class FileFilterResLine:
    def __init__(self, linenumber, line):
        self.mLineNumber = linenumber;
        self.mLine = line;
    def dump(self):
        print self.mLineNumber," :",self.mLine

class FileFilter:
    mFileName=""
    def __init__(self, filename):
        self.mFileName = filename;
        self.mFileLines = open(filename).readlines();
        if os.path.exists(filename):
            pass
        else:
            raise IOError(filename+"file isn't found")

    def getLineCnt(self):
        return len(self.mFileLines)

    def searchByLine(self,patern):
        for linenumber in range(len(self.mFileLines)):
            result = re.search(patern, self.getLine(linenumber));
            if result:
                mobj = FileFilterResLine(linenumber, result.group(0));
                return mobj;
        return "";

    def searchByWholeLine(self,str, startline=0):
        for linenumber in range(startline, len(self.mFileLines)):
            if str ==  self.getLine(linenumber)[:-1]:
                mobj = FileFilterResLine(linenumber, str);
                return mobj;
        return "";
    def getLine(self, index):
        return self.mFileLines[index]

    def searchByLine1(self,patern):
        "return:                \
            FileFilterResLine: mLineNumber: lineNumber; \
                               mLine:       line context"

        objlist=[]
        for linenumber in range(len(self.mFileLines)):
            result = re.search(patern, self.getLine(linenumber));
            if result:
                mobj = FileFilterResLine(linenumber, result.group(0));
                objlist.append(mobj)

        return objlist;

    def searchByRange(self,patern, start, end):
        objlist=[]
        for linenumber in range(start, end):
            result = re.search(patern, self.getLine(linenumber));
            if result:
                mobj = FileFilterResLine(linenumber, result.group(0));
                objlist.append(mobj)
        return objlist;

    def searchByMultiLines(self,linelist, n_startNum = 0):
        objlist=[]
        startline = linelist[0]

        for linenumber in range(n_startNum, len(self.mFileLines)):
            if startline == self.getLine(linenumber) \
                and linelist[1] == self.getLine(linenumber+1) \
                and linelist[2] == self.getLine(linenumber+2):

                    return str(linenumber)

        return ""

    def getLine(self, index):
        return self.mFileLines[index]

if __name__ == "__main__":
    obfile = FileFilter("/home/zoucao/github/linux-stable/patches/0200-net-core-datagram-Add-skb_copy_datagram_to_kernel_io.patch");
    print obfile.searchByLine('Subject.*$').mLine


