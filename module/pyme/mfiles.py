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

class FileFilter:
    mFileName=""
    def __init__(self, filename):
        self.mFileName = filename;
        self.mFileLines = open(filename).readlines();

    def searchByLine(self,patern):
        for linenumber in range(len(self.mFileLines)):
            result = re.search(patern, self.getLine(linenumber));
            if result:
                mobj = FileFilterResLine(linenumber, result.group(0));
                return mobj;
        return "";

    def getLine(self, index):
        return self.mFileLines[index]

if __name__ == "__main__":
    obfile = FileFilter("/home/zoucao/github/linux-stable/patches/0200-net-core-datagram-Add-skb_copy_datagram_to_kernel_io.patch");
    print obfile.searchByLine('Subject.*$').mLine


