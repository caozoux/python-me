#!/usr/bin/env python2.7
from mfiles import *;
import colorprint;

class patchModifyItem:
    def __init__(self, line, start):
        self.mStartLine= line;
        self.mStart= start;
        self.mPItemConList=[]
        #how many lines added in this item
        self.mAddNumber=0
        self.mDelNumber=0
        self.mType=""
        self.mCmpStartline=0

    def setFile(self, ofile):
        self.mFile = ofile;

    def bindPatchModifyFile(self, obj):
        self.mOPatch=obj;

    def setGitNum(self, num):
        self.mSrcNum = num;

    def setItemType(self,type):
        self.mType=type

    def analysis(self, patchFileList):
        "analysis the item of patch and format to list"
        patchItemEnd = ["@@ ", "dif", "-- "]
        self.mPItemConList.append(patchFileList[self.mStart][:-1]);

        #get the range of patch item
        for index in range(self.mStart+1, len(patchFileList)):
            line = patchFileList[index]
            if line[:3] == patchItemEnd[0] \
               or line[:3] == patchItemEnd[1] \
               or line[:3] == patchItemEnd[2] :
                self.mEnd=index-1;
                break;
            self.mPItemConList.append(line[:-1]);
            if line[0] == '+':
                self.mAddNumber += 1
            elif line[0] == '-':
                self.mDelNumber += 1

        #set file type: Makefile CFILE HFILE KCONFIG
        list=re.split('/+',self.mOPatch.mFilename)

        #set patch item type
        filetype=list[-1]
        if filetype == "Makefile":
            self.setItemType("Makefile")
        elif filetype[-2:-1] == ".c":
            self.setItemType("CFILE")
        elif filetype[-2:-1] == ".h":
            self.setItemType("HFILE")
        elif filetype == "Kconfig":
            self.setItemType("KCONFIG")

        for i in range(1,len(self.mPItemConList)):
            pass;

    def showItemAddDelpart(self, srcstart, patchstart):
        "flag : \
            1: merge "
        oFileFilter = FileFilter(self.mOPatch.mFilename)

        startline = patchstart
        for i in range(len(self.mPItemConList)):
            line = self.mPItemConList[i]
            if line[0] == '+':
                print "add new---> ",line
                print ""
            elif line[0] == ' ':
                print line[1:], srcstart
                print oFileFilter.getLine(srcstart)
                srcstart += 1
            elif line[0] == '-':
                print line[1:], srcstart
                print oFileFilter.getLine(srcstart)
                srcstart += 1

    def showSrcAndItem(self):
        startlist=[]
        ostartobj=[]
        endlist=[]
        oendobj=[]

        oFileFilter = FileFilter(self.mOPatch.mFilename)
        for i in range(1,4):
            startlist.append(self.mPItemConList[i][1:])
            mfileitem1 = oFileFilter.searchByWholeLine(startlist[i-1])
            if mfileitem1:
                ostartobj.append(mfileitem1)

            endlist.append(self.mPItemConList[i-4][1:])
            mfileitem1 = oFileFilter.searchByWholeLine(endlist[i-1])
            if mfileitem1:
                oendobj.append(mfileitem1)

        if len(ostartobj) == 3:
            if ostartobj[1].mLineNumber - ostartobj[0].mLineNumber == 1:
                if ostartobj[2].mLineNumber - ostartobj[1].mLineNumber == 1:
                    self.mCmpStartline = ostartobj[0].mLine
                    pass;
            elif ostartobj[2].mLineNumber - ostartobj[1].mLineNumber == 1:
                self.mCmpStartline = ostartobj[2].mLineNumber-2
            else:
                print "can't find start three lines"
                return

        self.showItemAddDelpart(self.mCmpStartline,0)

    def dump(self):
        colorprint.warn("patch item: "+self.mStartLine)
        #print self.mStartLine, self.mStart, self.mEnd, self.mSrcNum
        for line in self.mPItemConList:
            print "   "+line;

#diff iterm of patch 
class patchModifyFile:
    def __init__(self, start, end):
        self.start = start;
        self.end   = end;
        self.mPatchItem=[]

    def setFileName(self, filename):
        self.mFilename = filename

    def addPatchItem(self, oPatchItem):
        self.mPatchItem.append(oPatchItem)

    def dump(self):
        colorprint.info("file: "+self.mFilename)
        colorprint.info("start:"+str(self.start)+" end:"+str(self.end))
        for obj in self.mPatchItem:
            obj.dump()

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
        "save one diff item of patch to patchModifyFile"

        varlist = self.omfile.searchByLine1("diff --git a.*$")
        for index in range(len(varlist)):
            if index+1 < len(varlist):
                obj = patchModifyFile(varlist[index].mLineNumber, varlist[index+1].mLineNumber-1)
            else:
                res = self.omfile.searchByWholeLine("-- ")
                obj = patchModifyFile(varlist[index].mLineNumber, res.mLineNumber)

            res = re.sub('diff --git a.*\w b/', "", varlist[index].mLine)
            if res:
                obj.setFileName(res)
            else:
                obj.setFileName("")

        #handle last patch modify file
        res = re.sub('diff --git a.*\w b/', "", varlist[index].mLine)
        if res:
            obj.setFileName(res)
        else:
            obj.setFileName("")

        self.mFiles.append(obj)

    #format the patch, the modified files of patch saved into mFiles
    #the diff item of patch of mFIles saved into mPatchItem
    def formatPatch(self):
        self.formatPatchMFileToList();
        for objp in self.mFiles:
            varlist = self.omfile.searchByRange("^@@.*$",objp.start,objp.end)
            for obj in varlist:
                patchitem = patchModifyItem(obj.mLine, obj.mLineNumber)
                patchitem.setFile(self.mPatchName)
                patchitem.setGitNum(re.sub(',.*$',"",re.sub('^@@ -', "", obj.mLine)))
                patchitem.bindPatchModifyFile(objp)
                patchitem.analysis(self.omfile.mFileLines)
                self.mPatchItem.append(patchitem)
                objp.addPatchItem(patchitem)

    def analysis(self):
        "format the patch, split the patch to list objesc by modifed files \
        very modified files will create a patchModifyItem obj, it save the all diff timer of this file"
        self.formatPatch();

    def findPatchItemByLine(self, line):
        for item in self.mPatchItem:
            if line == item.mSrcNum:
                return item
        return "";

    def dump(self):
        for obj in self.mFiles:
            oPatchItem = obj.mPatchItem;
            obj.dump()
            #objp = obj.mfile;
            #print "modify filename: ",objp.mFilename, " range in patch:", objp.start,"~", objp.end
            #print "patch item: ", obj.mSrcNum

if __name__ == "__main__":
    test = patchcontext("/fslink/ti/kernel-4.1.x/patches/0195-dma-mv_memcpy-initial-driver-for-efficient-splice-me.patch")
    test.fileList();
    test.dump();
