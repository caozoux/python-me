#!/usr/bin/env python2.7
from mfiles import *;
import colorprint;
import leveldbg;
import patchop;

class patchConflictItem:
    def __init__(self, patchName, srcfile):
        self.mSrcFile_s=srcfile #src file name
        self.mPatch_s=patchName #patch file name
        self.mP_SLNumber_n=0 #the lines number start in patch
        self.mP_ELNumber_n=0 #the lines number end in patch
        self.mS_SLNumber_n=0 #the lines number start in code file
        self.mS_ELNumber_n=0 #the lines number end in code file 
        self.mPLines_ls=[]   # list lines of patch
        self.mSLines_ls=[]   # list lines of code file

    def setPatchContext(self, startNum, size):
        oFileFilter = FileFilter(self.mPatch_s)
        self.mP_SLNumber_n=startNum;
        self.mP_ELNumber_n=startNum+size;
        for i in range(size):
            line = oFileFilter.getLine(i+startNum)
            self.mPLines_ls.append(line)

    def setFileContext(self, startNum, size):
        oFileFilter = FileFilter(self.mSrcFile_s)
        self.mS_SLNumber_n=startNum;
        self.mS_ELNumber_n=startNum+size;
        #print startNum, size
        for i in range(size):
            line = oFileFilter.getLine(i+startNum)
            self.mSLines_ls.append(line)

    def isConflict(self):
        psize_n=self.mP_ELNumber_n-self.mP_SLNumber_n;
        ssize_n=self.mS_ELNumber_n-self.mS_SLNumber_n;
        line_max_size=max(psize_n,ssize_n)

        for i in range(line_max_size):
            if i < len(self.mPLines_ls):
                line_p =self.mPLines_ls[i]
            else:
                line_p=""

            if i < len(self.mSLines_ls):
                line_s =self.mSLines_ls[i]
            else:
                line_s=""

            if line_p[1:-1] != line_s[:-1]:
                return 1
        return 0

    def save(self):
        "save this modifoed to patch"
        #for i in range(self.mP_ELNumber_n-self.mP_SLNumber_n):
        size = (self.mP_ELNumber_n-self.mP_SLNumber_n)
        #os.system("sed -i '"+str(self.mS_SLNumber_n)+","+str(self.mP_ELNumber_n)+"d "+self.mPatch_s)
        #print("sed -i '"+str(self.mP_SLNumber_n+1)+",+"+str(self.mP_ELNumber_n-self.mP_SLNumber_n-1)+"d' "+self.mPatch_s)
        os.system("sed -i '"+str(self.mP_SLNumber_n+1)+",+"+str(self.mP_ELNumber_n-self.mP_SLNumber_n-1)+"d' "+self.mPatch_s)
        for i in range(len(self.mPLines_ls)):
            line=self.mPLines_ls[i].replace("/","\/")
            os.system("sed -r -i '"+str(self.mP_SLNumber_n+i)+"a \\ \\"+line[1:]+"' "+self.mPatch_s)

    def reConflictLines(self):
        "it replace the conflictLines with user select"

        psize_n=self.mP_ELNumber_n-self.mP_SLNumber_n;
        ssize_n=self.mS_ELNumber_n-self.mS_SLNumber_n;
        line_max_size=max(psize_n,ssize_n)

        for i in range(line_max_size):
            if i < len(self.mPLines_ls):
                line_p =self.mPLines_ls[i]
            else:
                line_p=""

            if i < len(self.mSLines_ls):
                line_s =self.mSLines_ls[i]
            else:
                line_s=""
            if line_p[1:-1] != line_s[:-1]:
                colorprint.err("Err:{:<90}".format("     "+line_p[:-1].replace("\t","    "))+"{:<20}".format("||  "+line_s[:-1].replace("\t","    ")))
                print "1. replace with src file"
                print "2. remove it"
                answer_a =raw_input("select: ")
                if answer_a == "1":
                    if line_s == "":
                        self.mSLines_ls.append(self.mSLines_ls[i][0]+line_s)
                    else:
                        self.mPLines_ls[i] = self.mPLines_ls[i][0]+line_s
                        self.save()
                        exit()
                elif answer_a == "2":
                    pass
                else:
                    return 

    def dump(self):
        #print "patchConflictItem dump:"
        psize_n=self.mP_ELNumber_n-self.mP_SLNumber_n;
        ssize_n=self.mS_ELNumber_n-self.mS_SLNumber_n;
        line_max_size=max(psize_n,ssize_n)

        for i in range(line_max_size):
            if i < len(self.mPLines_ls):
                line_p =self.mPLines_ls[i]
            else:
                line_p=""

            if i < len(self.mSLines_ls):
                line_s =self.mSLines_ls[i]
            else:
                line_s=""
            if line_p[1:-1] == line_s[:-1]:
                colorprint.blue("{:<90}".format("PASS "+line_p[:-1].replace("\t","    "))+"{:<20}".format("||  "+line_s[:-1].replace("\t","    ")))
            else:
                colorprint.err("{:<90}".format("     "+line_p[:-1].replace("\t","    "))+"{:<20}".format("||  "+line_s[:-1].replace("\t","    ")))

        return

#patchModifyItem
#bindPatchModifyFile(self, obj):
#setGitNum(self, num):
#setItemType(self,type):
#analysis(self, patchFileList):

#dump_patch(self)
#  print the patch context and confilct with code file
#dump(self)
#
#rmInPatch(self):
#    rm this item in patch file 
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
        self.mOSrcLines=[]  #it the patch item code line that is exist in src file
        self.mLStartList_s=[] #it save the 3S lines of patch item
        self.mLEndList_s=[]   #it save the 3E lines of patch item
        self.mLoStartList_s=[] #it save the 3S lines of code file
        self.mLoEndList_s=[]   #it save the 3E lines of code file
        self.mSrcLineS_n=0     #it save the 3S lines Start number of code file
        self.mSrcLineE_n=0     #it save the 3S lines Start number of code file

    def setFile(self, ofile):
        self.mFile = ofile;

    def bindPatchModifyFile(self, obj):
        self.mOPatch=obj;

    def setGitNum(self, num):
        self.mSrcNum = num;

    def setItemType(self,type):
        self.mType=type

    def saveModifyItem(self):
        print self.mFile, self.mStart
        oFileFilter = FileFilter(self.mFile) 
        for i in range(len(self.mPItemConList)):
            line = oFileFilter.getLine(i+self.mStart)
            if line[:-1] != self.mPItemConList[i]:
                print "is different"
                print line[:-1],  self.mPItemConList[i]
                os.system("sed -i 's/"+line[:-1]+"/"+self.mPItemConList[i].replace("/","\/")+"/' "+self.mFile);

    def getSrcCode(self):
        "get the line list of \"-xxxx\" code in patch item"

        if len(self.mOSrcLines) !=0:
            return;

        lineList=[]
        for line in self.mPItemConList:
            if line[0] == "-" or line[0] == " ":
                self.mOSrcLines.append(line);

    def findInSrcCode(self, line_s):
        "get the line list of \"-xxxx\" code in patch item"
        for i in range(len(self.mOSrcLines)):
            line = self.mOSrcLines[i]
            #print line[1:], line_s
            if line[1:] == line_s:
                return i
        return -1;

    def rePatchSrc(self):
        "replace the conflict line with src code"
        print_out=""
        pushdown_cnt_src = 0
        pushdown_cnt_patch = 1
        pushdown_cnt_src_last = 0
        pushdown_cnt_patch_last = 4
        srcSandELines=[] #it save the lines of src file between item 3S and 3E
        srcLine=""  #it save the src context of one line
        patchLine="" #it save the patch context of one line
        oFileFilter = FileFilter(self.mOPatch.mFilename)
        cmp_cnt=[]


        # start compare the patch with code file, splite the different to cmp_cnt
        for i in range(int(self.mSrcLineS_n), int(self.mSrcLineE_n)+3):
            line = oFileFilter.getLine(i);
            srcSandELines.append(line)
            res=self.findInSrcCode(line[:-1])
            if res != -1:
                for j in range(pushdown_cnt_patch, len(self.mPItemConList)):
                    patchLine = self.mPItemConList[j]
                    if patchLine[1:] == line[:-1]:
                        find_cnt=[]
                        find_cnt.append(i-(int(self.mSrcLineS_n)))
                        find_cnt.append(j)
                        cmp_cnt.append(find_cnt)
                        pushdown_cnt_patch = j
                        pushdown_cnt_src = i-(int(self.mSrcLineS_n));
                        break

        last_num_s = 0
        last_num_p = 1
        for i in range(len(cmp_cnt)):
            size=0
            obj_s = cmp_cnt[i]
            oPatchConflictItem = patchConflictItem(self.mFile, self.mOPatch.mFilename)
            oPatchConflictItem.setPatchContext(last_num_p+self.mStart,obj_s[1]-last_num_p)
            oPatchConflictItem.setFileContext(last_num_s+(int(self.mSrcLineS_n)),obj_s[0]-last_num_s)
            oPatchConflictItem.dump()
            last_num_s = obj_s[0]
            last_num_p = obj_s[1]

            if oPatchConflictItem.isConflict():
                print "1. replace"
                print "2. rm item"

                answer=raw_input("select:")
                if answer == "1":
                    oPatchConflictItem.reConflictLines()
                elif answer == "2":
                    self.mPItemConList.remove(i+last_num_p+1)
                    answer=raw_input("Do you want to save y/n:")
                    if answer == "y":
                        self.saveModifyItem()
                    else:
                        return
                else:
                    return
        return
        self.dump_patch()



    def rmInPatch(self):
        "rm this modify item in patch file"
        needRmFileTag=0
        oFileFilter = FileFilter(self.mFile)

        #show the patch item
        for i in range(self.mStart, self.mEnd):
            line = oFileFilter.getLine(i)
            print line[:-1]
        answer=raw_input("are you sure to rm these y/n?:")
        if answer == "y":
            line = oFileFilter.getLine(self.mStart-1)
            res=re.search("^\+\+\+ b*", line)
            if res:
                line = oFileFilter.getLine(self.mEnd+1)
                res=re.search("^diff \-\-git a", line)
                if res:
                    needRmFileTag=1

        os.system("sed -i \""+str(self.mStart+1)+","+str(self.mEnd+1)+"d\" "+self.mFile)
        if needRmFileTag == 1:
            for i in range(self.mStart-4, self.mStart):
                print oFileFilter.getLine(i)[:-1]
            answer=raw_input("are you sure to rm these, the file patch will be ignore y/n?:")
            if answer == "y":
                os.system("sed -i \""+str(self.mStart-4)+","+str(self.mStart)+"d\" "+self.mFile)

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
        #patchItemTarg save the patch item targe::@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg=""

        try:
            oFileFilter = FileFilter(self.mOPatch.mFilename)
        except IOError:
            colorprint.err(self.mOPatch.mFilename+" isn't found")
            #self.dump()
            return

        print "dump patch:"
        self.getSrcCode()

        #search this in patch file:@ -1825,7 +1825,7 @@ config FB_PS3_DEFAULT_SIZE_M
        patchItemTarg = re.sub('^@.*@@\s', "", self.mPItemConList[0][1:])
        oCmpLine= oFileFilter.searchByWholeLine(patchItemTarg)
        if oCmpLine== "":
            colorprint.err(self.mStartLine)
            colorprint.err("ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")
            self.dump()
            answer=raw_input("Do you want to continue y/n? ")
            if answer == "y":
                pass
            else:
                return

        print("{:=<80}".format(self.mOPatch.mFilename)+"{:=<80}".format(self.mPItemConList[0][1:]))
        #patch three lines
        for i in range(1,4):
            if self.mPItemConList[i][-1] != "\n":
                self.mLStartList_s.append(self.mPItemConList[i][1:]+"\n")
            else:
                self.mLStartList_s.append(self.mPItemConList[i][1:])

            if self.mPItemConList[i-4][-1] != "\n":
                self.mLEndList_s.append(self.mPItemConList[i-4][1:]+"\n")
            else:
                self.mLEndList_s.append(self.mPItemConList[i-4][1:])

        #patch 3s lines, it is start cmp line number
        self.mSrcLineS_n = oFileFilter.searchByMultiLines(self.mLStartList_s)
        if self.mSrcLineS_n:
            self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)))
            self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)+1))
            self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)+2))
        else:
            self.mSrcLineS_n = patchcontext.patchConflict3Ls(self, self.mLStartList_s)
            if self.mSrcLineS_n == -1:
                colorprint.err("not find the patch item start");
                self.dump()
                return 0;
            else:
                self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)))
                self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)+1))
                self.mLoStartList_s.append(oFileFilter.getLine(int(self.mSrcLineS_n)+2))

        for i in range(0,3):
            #print "%-70s%-20s" %(self.mLStartList_s[i], self.mLoStartList_s[i].mLine)
            if self.mLStartList_s[i] != self.mLoStartList_s[i]:
                colorprint.err("{:<90}".format(self.mLStartList_s[i][1:-1])+"{:<20}".format("||  "+self.mLoStartList_s[i][1:-1]))
            else:
                colorprint.info("{:<90}".format(self.mLStartList_s[i][1:-1])+"{:<20}".format("||  "+self.mLoStartList_s[i][1:-1]))

        #patch 3e lines
        self.mSrcLineE_n = oFileFilter.searchByMultiLines(self.mLEndList_s)
        if self.mSrcLineE_n:
            self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)))
            self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)+1))
            self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)+2))
        else:
            self.mSrcLineE_n= patchcontext.patchConflict3Ls(self, self.mLEndList_s)
            if self.mSrcLineE_n== -1:
                colorprint.err("not find the patch item start");
                self.dump()
                return 0;
            else:
                self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)))
                self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)+1))
                self.mLoEndList_s.append(oFileFilter.getLine(int(self.mSrcLineE_n)+2))

        print_out=""
        pushdown_cnt_src = 0
        pushdown_cnt_patch = 4
        pushdown_cnt_src_last = 0
        pushdown_cnt_patch_last = 4
        i = int(self.mSrcLineS_n)+3 #start cmp line number
        srcSandELines=[] #it save the lines of src file between item 3S and 3E
        srcLine=""  #it save the src context of one line
        patchLine="" #it save the patch context of one line

        var=0
        cmp_cnt=[]
        for i in range(int(self.mSrcLineS_n)+3, int(self.mSrcLineE_n)):
            line = oFileFilter.getLine(i);
            srcSandELines.append(line)
            res=self.findInSrcCode(line[:-1])
            if res != -1:
                for j in range(pushdown_cnt_patch, len(self.mPItemConList)-3):
                    patchLine = self.mPItemConList[j]
                    if patchLine[1:] == line[:-1]:
                        find_cnt=[]
                        find_cnt.append(i-(int(self.mSrcLineS_n)+3))
                        find_cnt.append(j)
                        cmp_cnt.append(find_cnt)
                        pushdown_cnt_patch = j
                        pushdown_cnt_src = i-(int(self.mSrcLineS_n)+3);

        last_num_s = 0
        last_num_p = 3
        for i in range(len(cmp_cnt)):
            size=0
            obj_s = cmp_cnt[i]

            if (obj_s[0]-last_num_s) > (obj_s[1]-last_num_p):
                size=obj_s[0]-last_num_s
            else:
                size=obj_s[1]-last_num_p

            #print obj_s[0], obj_s[1], size
            for i in range(size):
                if i == (size-1):
                    line_s = srcSandELines[obj_s[0]]
                    line_p = self.mPItemConList[obj_s[1]]
                    colorprint.blue("{:<90}".format(line_p.replace("\t","    "))+"{:<20}".format("||  "+line_s[:-1].replace("\t","    ")))
                else:
                    if i < (obj_s[0]-last_num_s):
                        line_s = srcSandELines[i+last_num_s+1]
                    else:
                        line_s=""

                    if i < (obj_s[1]-last_num_p):
                        line_p = self.mPItemConList[i+last_num_p+1]
                    else:
                        line_p=""
                    colorprint.err("{:<90}".format(line_p.replace("\t","    "))+"{:<20}".format("||  "+line_s[:-1].replace("\t","    ")))

            last_num_s = obj_s[0]
            last_num_p = obj_s[1]

        if pushdown_cnt_src == 0:
            #not find any match src line in patch item,
            #print all lines 
            for i in range(len(srcSandELines)):
                colorprint.err("{:<90}".format("")+"{:<20}".format("<<  "+srcSandELines[i][:-1]))
            pushdown_cnt_src = len(srcSandELines);

        #print "zz",pushdown_cnt_patch, len(self.mPItemConList)-3
        #contine to show the conflict
        for i in range(pushdown_cnt_patch, len(self.mPItemConList)-4):
            patchLine = self.mPItemConList[i]
            if patchLine[0] == "-":
                for j in range(pushdown_cnt_src, len(srcSandELines)):
                    if patchLine[1:] == srcSandELines[j]:
                        colorprint.info("{:<90}".format(patchLine[:-1])+"{:<20}".format("||  "+srcSandELines[i][:-1]))
                        pushdown_cnt_src = j
                    else:
                        colorprint.info("{:<90}".format(patchLine[1:-1])+"{:<20}".format("||  "))
                    continue
            elif patchLine[0] == "+":
                colorprint.warn("{:<90}".format(patchLine[:-1].replace("\t","    "))+"{:<20}".format(">>  "))
                #colorprint.warn(patchLine[:-1])
            elif patchLine[0] == " ":
                colorprint.info("{:<90}".format(patchLine[:-1]))
            else:
                colorprint.err("err: patch is not right")
                return

        #for i  in range(pushdown_cnt_patch, len(srcSandELines)):
            #colorprint.err("{:<90}".format("")+"{:<20}".format("<<  "+srcSandELines[i]))

        for i in range(0,3):
            #print "%-70s%-20s" %(self.mLStartList_s[i], self.mLoStartList_s[i].mLine)
            if self.mLEndList_s[i] != self.mLoEndList_s[i]:
                colorprint.err("{0:90}".format(self.mLEndList_s[i][1:-1])+"{0:20}".format("||  "+self.mLoEndList_s[i][1:-1]))
            else:
                colorprint.info("{0:90}".format(self.mLEndList_s[i][1:-1])+"{0:20}".format("||  "+self.mLoEndList_s[i][1:-1]))

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
        len1=0
        len2=0
        len3=0
        nStartLine = 0;

        oFileFilter = FileFilter(oPatchModifyItem.mOPatch.mFilename)

        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        mfileitem1 = oFileFilter.searchByWholeLine(patchItemTarg)
        if mfileitem1 == "":
            colorprint.warn("Warning: patchConflict3Ls TAG:-->"+patchItemTarg+"<--NOT FIND")
            nStartLine = 0;
        else:
            nStartLine = mfileitem1.mLineNumber;

        s_src = oFileFilter.searchByMultiLines(L3s)
        if s_src:
            return s_src
        else:
            len1=len(L3s[0])
            len2=len(L3s[1])
            len3=len(L3s[2])

            #first search L3s0/L3s1, then L3s1/L3s2
            for i in range(2):
                line2List=[]
                line2List.append(L3s[0+i])
                line2List.append(L3s[1+i])
                s_src = oFileFilter.searchByMultiLines(line2List,0,2)
                if s_src:
                    return str(int(s_src)-i)

            #try to find max len in L3s
            index = 0
            size=0
            for i  in range(3):
                if len(L3s[i]) > size:
                    size = len(L3s[i])
                    index = i

            oLine1 =oFileFilter.searchByWholeLine(L3s[index], nStartLine)
            if oLine1:
                return oLine1.mLineNumber

            for i in range(3):
                if len(L3s[i]) < 3:
                    continue
                oLine1 =oFileFilter.searchByWholeLine(L3s[i], nStartLine)
                if oLine1:
                    return oLine1.mLineNumber
        return -1

    @staticmethod
    def patchConflict3es(gitsrc, commit, shorLogBuf):
        pass

if __name__ == "__main__":
    test = patchcontext("/fslink/ti/kernel-4.1.x/patches/0195-dma-mv_memcpy-initial-driver-for-efficient-splice-me.patch")
    test.fileList();
    test.dump();
