#!/usr/bin/env python2.7
from mfiles import *;

class patchModifyItem:
    def __init__(self, line, start):
        self.mStartLine= line;
        self.mStart= start;

    def setFile(self, ofile):
        self.mFile = ofile;
    def setGitNum(self, num):
        self.mSrcNum = num;

    def anaalysis(self, patchFileList):
        patchItemEnd = ["@@ ", "dif", "-- "]
        "patchFileList: patch context lines list"
        for index in range(self.mStart+1, len(patchFileList)):
            line = patchFileList[index]
            if line[:3] == patchItemEnd[0] \
               or line[:3] == patchItemEnd[1] \
               or line[:3] == patchItemEnd[2] :
                self.mEnd=index-1;
                break;

        pass;

    def dump(self):
        print self.mStartLine, self.mStart, self.mEnd, self.mSrcNum

#patch modify file name
class patchModifyFile:
    def __init__(self, start, end):
        self.start = start;
        self.end   = end;

    def setFileName(self, filename):
        self.mFilename = filename

class patchcontext:

    def __init__(self, patchname):
        self.mPatchName=patchname
        #patch name
        self.omfile = FileFilter(patchname)
        #it is the patch modify file name
        self.mFiles=[]
        # patch modify items list
        self.mPatchItem=[]
    def formatPatchMFileToList(self):
        varlist = self.omfile.searchByLine1("diff --git a.*$")
        for index in range(len(varlist)-1):
            obj = patchModifyFile(varlist[index].mLineNumber, varlist[index+1].mLineNumber-1)
            res = re.sub('diff --git a.*\w b/', "", varlist[index].mLine)
            if res:
                obj.setFileName(res)
            else:
                obj.setFileName("")
            self.mFiles.append(obj)
        #handle last patch modify file
        obj = patchModifyFile(varlist[len(varlist)-1].mLineNumber, len(self.omfile.mFileLines))
        res = re.sub('diff --git a.*\w b/', "", varlist[index].mLine)
        if res:
            obj.setFileName(res)
        else:
            obj.setFileName("")
        self.mFiles.append(obj)

    #format the patch modify item to obj list patchModifyItem
    def formatPatchMItemToList(self):
        self.formatPatchMFileToList();
        for objp in self.mFiles:
            varlist = self.omfile.searchByRange("^@@.*$",objp.start,objp.end)
            for obj in varlist:
                patchitem = patchModifyItem(obj.mLine, obj.mLineNumber)
                patchitem.setFile(self.mPatchName)
                patchitem.setGitNum(re.sub(',.*$',"",re.sub('^@@ -', "", obj.mLine)))
                patchitem.anaalysis(self.omfile.mFileLines)
                self.mPatchItem.append(patchitem)

    def analysis(self):
        self.formatPatchMFileToList();
        self.formatPatchMItemToList();

    def findPatchItemByLine(self, line):
        for item in self.mPatchItem:
            if line == item.mSrcNum:
                return item
        return "";

    def dump(self):
        for obj in self.mPatchItem:
            objp = obj.ofile;
            print "modify filename: ",objp.mFilename, " range in patch:", objp.start,"~", objp.end
            print "patch item: ", obj.mSrcNum

if __name__ == "__main__":
    test = patchcontext("/fslink/ti/kernel-4.1.x/patches/0195-dma-mv_memcpy-initial-driver-for-efficient-splice-me.patch")
    test.fileList();
    test.dump();
