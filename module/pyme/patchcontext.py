#!/usr/bin/env python2.7
from mfiles import *;
import colorprint;
import leveldbg;
import patchop;

#patchModifyItem
#bindPatchModifyFile(self, obj):
#setGitNum(self, num):
#setItemType(self,type):
#analysis(self, patchFileList):

#dump_patch(self)
#  print the patch context and confilct with code file
#dump(self)
class patchModifyItem:
    def __init__(self, line, start):
        self.mStartLine= line;
        self.mStart= start;
        self.mPItemConList=[]  #it is the context of patch item
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

    def checkAddline(self, srcfile):
        oFileFilter = FileFilter(srcfile+"/"+self.mOPatch.mFilename)
        addLines=[]
        for line in self.mPItemConList:
            if line[0] == "+":
                resLine = oFileFilter.searchByWholeLine(line[1:])
                if not resLine:
                    #words = line[1:].split("[ \t]")
                    words = re.split("[ \t]", line[1:])
                    if words[0] == "#define":
                        resLine = oFileFilter.searchByLine(words[1])
                        colorprint.blue("Find:"+srcfile+"/"+self.mOPatch.mFilename+":"+str(resLine.mLineNumber))
                        print line[:-1]
                    else:
                        #print "Not find "+line[1:0]+" in "+srcfile+"/"+self.mOPatch.mFilename
                        pass


    def dump_patch(self):
        startlist=[]
        ostartobj=[]
        endlist=[]
        oendobj=[]
        #patchItemTarg save the patch item targe::@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg=""
        try:
            oFileFilter = FileFilter(self.mOPatch.mFilename)
        except IOError:
            colorprint.err(self.mOPatch.mFilename+" isn't found")
            #self.dump()
            return
        #1 no conflict, 1 line1 and line2 is okay 
        #2 line2 and line3 is okay
        #3 line1 and line3 is okay
        #4 just and line1 is okay
        #5 just and line2 is okay
        #6 just and line3 is okay
        fristCmp_conflict_mode = 0

        #search this in patch file:@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg = re.sub('^@.*@@\s', "", self.mPItemConList[0][1:])
        oCmpLine= oFileFilter.searchByWholeLine(patchItemTarg)
        if oCmpLine== "":
            colorprint.err(self.mStartLine)
            colorprint.err("ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")
            return

        #mfileitem1 = oFileFilter.searchByWholeLine(startlist[0])
        #if mfileitem1:
        #    ostartobj.append(mfileitem1)

        print("{:=<80}".format(self.mOPatch.mFilename)+"{:=<80}".format(self.mPItemConList[0][1:]))
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

        #patch 3s lines, it is start cmp line number
        s_srcCmp = oFileFilter.searchByMultiLines(startlist)
        if s_srcCmp:
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+1))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+2))
        else:
            s_srcCmp = patchcontext.patchConflict3Ls(self, startlist)
            if s_srcCmp == -1:
                colorprint.err("not find the patch item start");
                self.dump()
                return 0;

        patch_src_line = []
        for i in range(4, len(self.mPItemConList)-3):
            line = self.mPItemConList[i]
            if line[0] == "-":
                patch_src_line.append(line)

        for i in range(0,3):
            #print "%-70s%-20s" %(startlist[i], ostartobj[i].mLine)
            if startlist[i] != ostartobj[i]:
                colorprint.err("{:<90}".format(startlist[i][1:-1])+"{:<20}".format("||  "+ostartobj[i][1:-1]))
            else:
                colorprint.info("{:<90}".format(startlist[i][1:-1])+"{:<20}".format("||  "+ostartobj[i][1:-1]))

        #patch 3e lines
        s_endCmp = oFileFilter.searchByMultiLines(endlist)
        if s_endCmp:
            oendobj.append(oFileFilter.getLine(int(s_endCmp)))
            oendobj.append(oFileFilter.getLine(int(s_endCmp)+1))
            oendobj.append(oFileFilter.getLine(int(s_endCmp)+2))

        print_out=""
        pushdown_cnt = 0
        i = int(s_srcCmp)+3 #start cmp line number
        srcSandELines=[] #it save the lines of src file between item 3S and 3E
        srcLine=""  #it save the src context of one line
        patchLine="" #it save the patch context of one line

        var=0
        #let the first conflict to print, then set the var of pushdown_cnt 
        for i in range(int(s_srcCmp)+3, int(s_endCmp)):
            line = oFileFilter.getLine(i);
            #srcSandELines.append(oFileFilter.getLine(i))
            srcSandELines.append(line)
            #print_out = "{:<90}".format("")+"{:<20}".format("<<  "+line)
            for j in range(4, len(self.mPItemConList)-3):
                patchLine = self.mPItemConList[j]
                if patchLine[1:] == line:
                    var = j
                    pushdown_cnt = i;
                    print_out = "{:<90}".format("")+"{:<20}".format("||  "+line)
                    break;

        if pushdown_cnt == 0:
            #not find any match src line in patch item,
            #print all lines 
            for i in range(len(srcSandELines)):
                colorprint.err("{:<90}".format("")+"{:<20}".format("<<  "+srcSandELines[i][:-1]))
            pushdown_cnt = len(srcSandELines);

        #contine to show the conflict
        for i in range(4, len(self.mPItemConList)-3):
            patchLine = self.mPItemConList[i]
            if patchLine[0] == "-":
                for j in range(pushdown_cnt, len(srcSandELines)):
                    if patchLine[1:] == srcSandELines[j]:
                        colorprint.info("{:<90}".format(patchLine[1:-1])+"{:<20}".format("||  "+srcSandELines[i][:-1]))
                        pushdown_cnt = j
                        continue
            elif patchLine[0] == "+":
                colorprint.warn("{:<90}".format(patchLine[:-1].replace("\t","    "))+"{:<20}".format(">>  "))
                #colorprint.warn(patchLine[:-1])
            elif patchLine[0] == " ":
                colorprint.info("{:<90}".format(patchLine[:-1]))
            else:
                colorprint.err("err: patch is not right")
                return

        for i  in range(pushdown_cnt, len(srcSandELines)):
            colorprint.err("{:<90}".format("")+"{:<20}".format("<<  "+srcSandELines[i]))

        for i in range(0,3):
            #print "%-70s%-20s" %(startlist[i], ostartobj[i].mLine)
            if endlist[i] != oendobj[i]:
                colorprint.err("{0:90}".format(endlist[i][1:-1])+"{0:20}".format("||  "+oendobj[i][1:-1]))
            else:
                colorprint.info("{0:90}".format(endlist[i][1:-1])+"{0:20}".format("||  "+oendobj[i][1:-1]))

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
                #print "dbg find file:"+res
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
        #colorprint.info("{:<90}".format(self.mPatchName)+"{:<20}".format("||  "+self.mFiles))
        print self.omfile.mFileName
        for oPatchModifyItem in self.mPatchItem:
            oPatchModifyItem.dump_patch()

    @staticmethod
    def patchConflict3Ls(oPatchModifyItem, L3s):
        oLine1 = ""
        oLine2 = ""
        oLine3 = ""
        nStartLine = 0;

        oFileFilter = FileFilter(oPatchModifyItem.mOPatch.mFilename)

        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        mfileitem1 = oFileFilter.searchByWholeLine(patchItemTarg)
        if mfileitem1 == "":
            colorprint.err("patchConflict3Ls ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")
            return -1;
        nStartLine = mfileitem1.mLineNumber;

        s_src = oFileFilter.searchByMultiLines(L3s)
        if s_src:
            return s_src
        else:
            oLine1 =oFileFilter.searchByWholeLine(L3s[0], nStartLine)
            if oLine1:
                return oLine1.mLineNumber
            else:
                oLine2 =oFileFilter.searchByWholeLine(L3s[1], nStartLine)
                if oLine2:
                    if oLine2.mLineNumber>1:
                        return oLine2.mLineNumber-1
                    else:
                        return oLine2.mLineNumber
                else:
                    oLine3 =oFileFilter.searchByWholeLine(L3s[2], nStartLine)
                    if oLine3:
                        if oLine3.mLineNumber>2:
                            return oLine1.mLineNumber-2
                        else:
                            return oLine1.mLineNumber
                    else:
                        return -1;
                    return -1

    @staticmethod
    def patchConflict3es(gitsrc, commit, shorLogBuf):
        pass

if __name__ == "__main__":
    test = patchcontext("/fslink/ti/kernel-4.1.x/patches/0195-dma-mv_memcpy-initial-driver-for-efficient-splice-me.patch")
    test.fileList();
    test.dump();
