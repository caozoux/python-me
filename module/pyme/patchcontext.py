#!/usr/bin/env python2.7
from mfiles import *;
import colorprint;
import leveldbg;
import patchop;

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
                colorprint.warn(line+"       <----add new")
                print ""
            elif line[0] == ' ':
                #print line[1:], srcstart
                print oFileFilter.getLine(srcstart)
                srcstart += 1
            elif line[0] == '-':
                #print line[1:], srcstart
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
                    #self.mCmpStartline = ostartobj[0].mLine
                    self.mCmpStartline = ostartobj[0].mLineNumber
                    pass;
            elif ostartobj[2].mLineNumber - ostartobj[1].mLineNumber == 1:
                self.mCmpStartline = ostartobj[2].mLineNumber-2
            else:
                print "can't find start three lines"
                return

        self.showItemAddDelpart(self.mCmpStartline,0)

    def dump_patch(self):
        startlist=[]
        ostartobj=[]
        endlist=[]
        oendobj=[]
        #patchItemTarg save the patch item targe::@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg=""
        oFileFilter = FileFilter(self.mOPatch.mFilename)
        #1 no conflict, 1 line1 and line2 is okay 
        #2 line2 and line3 is okay
        #3 line1 and line3 is okay
        #4 just and line1 is okay
        #5 just and line2 is okay
        #6 just and line3 is okay
        fristCmp_conflict_mode = 0

        #search this in patch file:@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg = re.sub('^@.*@@\s', "", self.mPItemConList[0][1:])
        mfileitem1 = oFileFilter.searchByWholeLine(patchItemTarg)
        if mfileitem1 == "":
            colorprint.err(self.mStartLine)
            colorprint.err("ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")
            return

        #mfileitem1 = oFileFilter.searchByWholeLine(startlist[0])
        #if mfileitem1:
        #    ostartobj.append(mfileitem1)

        #patch three lines
        for i in range(1,4):
            if self.mPItemConList[i][-1] != "\n":
                startlist.append(self.mPItemConList[i][1:]+"\n")
            else:
                startlist.append(self.mPItemConList[i][1:])

            if self.mPItemConList[i-4][-1] != "\n":
                endlist.append(self.mPItemConList[i-4][1:]+"\n")
            else:
                endlist.append(self.mPItemConList[i-4][1:])

        #start check the start three line 
        #trt to compare the patch three lines with src file, then get set fristCmp_conflict_mode value

        #patch 3s lines
        s_srcCmp = oFileFilter.searchByMultiLines(startlist)
        if s_srcCmp:
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+1))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+2))

        for i in range(0,3):
            #print "%-70s%-20s" %(startlist[i], ostartobj[i].mLine)
            if startlist[i] != ostartobj[i]:
                colorprint.err("{:<90}".format(startlist[i][1:-1])+"{:<20}".format("||  "+ostartobj[i][1:-1]))
            else:
                colorprint.info("{:<90}".format(startlist[i][1:-1])+"{:<20}".format("||  "+ostartobj[i][1:-1]))

        for i in range(4, len(self.mPItemConList)-3):
            colorprint.warn("{:<85}".format(self.mPItemConList[i])+"{:<20}".format("||  "))
            #print  self.mPItemConList[i]

        #patch 3e lines
        s_endCmp = oFileFilter.searchByMultiLines(endlist)
        if s_endCmp:
            oendobj.append(oFileFilter.getLine(int(s_endCmp)))
            oendobj.append(oFileFilter.getLine(int(s_endCmp)+1))
            oendobj.append(oFileFilter.getLine(int(s_endCmp)+2))

        for i in range(0,3):
            #print "%-70s%-20s" %(startlist[i], ostartobj[i].mLine)
            if endlist[i] != oendobj[i]:
                colorprint.err("{0:90}".format(endlist[i][1:-1])+"{0:20}".format("||  "+oendobj[i][1:-1]))
            else:
                colorprint.info("{0:90}".format(endlist[i][1:-1])+"{0:20}".format("||  "+oendobj[i][1:-1]))
        exit()

    def dump(self):
        colorprint.warn("patch item: "+self.mStartLine)
        for i in range(1,4):
            colorprint.info("   "+self.mPItemConList[i])
        #for line in self.mPItemConList:
        for i in range(4,len(self.mPItemConList)-3):
            print "   "+self.mPItemConList[i];
        for i in range(1,4):
            colorprint.info("   "+self.mPItemConList[i-4])

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

        leveldbg.dbg("dbg formatPatchMFileToList+")
        varlist = self.omfile.searchByLine1("diff --git a.*$")
        for index in range(len(varlist)):
            if index+1 < len(varlist):
                obj = patchModifyFile(varlist[index].mLineNumber, varlist[index+1].mLineNumber-1)
            else:
                res = self.omfile.searchByWholeLine("-- ")
                obj = patchModifyFile(varlist[index].mLineNumber, res.mLineNumber)

            res = re.sub('diff --git a.*\w b/', "", varlist[index].mLine)
            if res:
                print "dbg find file:"+res
                obj.setFileName(res)
                self.mFiles.append(obj)
            else:
                obj.setFileName("")

        leveldbg.dbg("dbg formatPatchMFileToList-")

    #format the patch, the modified files of patch saved into mFiles
    #the diff item of patch of mFiles saved into mPatchItem
    def formatPatch(self):
        leveldbg.dbg("dbg formatPatch+") #dbg
        self.formatPatchMFileToList();
        for objp in self.mFiles:
            leveldbg.dbg("dbg "+objp.mFilename)
            varlist = self.omfile.searchByRange("^@@.*$",objp.start,objp.end)
            for obj in varlist:
                patchitem = patchModifyItem(obj.mLine, obj.mLineNumber)
                patchitem.setFile(self.mPatchName)
                patchitem.setGitNum(re.sub(',.*$',"",re.sub('^@@ -', "", obj.mLine)))
                patchitem.bindPatchModifyFile(objp)
                patchitem.analysis(self.omfile.mFileLines)
                self.mPatchItem.append(patchitem)
                objp.addPatchItem(patchitem)
        leveldbg.dbg("dbg formatPatch-")

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

    def dump_patch(self):
        for oPatchModifyItem in self.mPatchItem:
            oPatchModifyItem.dump_patch()

if __name__ == "__main__":
    test = patchcontext("/fslink/ti/kernel-4.1.x/patches/0195-dma-mv_memcpy-initial-driver-for-efficient-splice-me.patch")
    test.fileList();
    test.dump();
