#!/usr/bin/env python2.7
from mfiles import *;
import colorprint

#check3Lines(lineList, target_git_dir):
# lineList: 3 line string list
# target_git_dir: target git tree
class patchMerge:
    def __init__(self,opatchitem,srcfilename):
        self.mOPatchItem = opatchitem
        self.mSrcFile = srcfilename
        #SFULL SMIDLE $LOW
        self.mModeStart=""

    
    @staticmethod
    def check3Lines(lineList, codeFile, target_git_dir):
        startlist=[]
        ostartobj=[]

        try:
            oFileFilter = FileFilter(codeFile)
        except IOError:
            colorprint.err(codeFile+" isn't found")
            return

        #check the 3S can be found in code file
        s_srcCmp = oFileFilter.searchByMultiLines(lineList)
        if s_srcCmp:
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+1))
            ostartobj.append(oFileFilter.getLine(int(s_srcCmp)+2))
            for i in range(0,3):
                if lineList[i] != ostartobj[i]:
                    colorprint.err("{:<90}".format(lineList[i][:-1].replace("\t","    "))+"{:<20}".format("||  "+ostartobj[i][:-1]))
                else:
                    colorprint.info("{:<90}".format(lineList[i][:-1].replace("\t","    "))+"{:<20}".format("||  "+ostartobj[i][:-1])+oFileFilter.mFileName+":"+str(int(s_srcCmp)+i))
        else:
            oSLine1 = oFileFilter.searchByWholeLine(lineList[0].replace("\t","    "))
            if oSLine1:
                colorprint.info("{:<90}".format(lineList[0][:-1].replace("\t","    "))+"{:<20}".format("||  "+oSLine1.mLine[1:-1])+oFileFilter.mFileName+":"+str(oSLine1.mLineNumber))
            else:
                colorprint.err("{:<90}".format(lineList[0][:-1].replace("\t","    "))+"{:<20}".format("||  S0 not find "+oFileFilter.mFileName))

            oSLine2 = oFileFilter.searchByWholeLine(lineList[1].replace("\t","    "))
            if oSLine2:
                colorprint.info("{:<90}".format(lineList[1][:-1].replace("\t","    "))+"{:<20}".format("||  "+oSLine2.mLine[1:-1])+oFileFilter.mFileName+":"+str(oSLine1.mLineNumber))
            else:
                colorprint.err("{:<90}".format(lineList[1][:-1].replace("\t","    "))+"{:<20}".format("||  S1 not find "+oFileFilter.mFileName))

            oSLine3 = oFileFilter.searchByWholeLine(lineList[2].replace("\t","    "))
            if oSLine3:
                colorprint.info("{:<90}".format(lineList[2][:-1].replace("\t","    "))+"{:<20}".format("||  "+oSLine3.mLine[1:-1])+oFileFilter.mFileName+":"+str(oSLine1.mLineNumber))
            else:
                colorprint.err("{:<90}".format(lineList[2][:-1].replace("\t","    "))+"{:<20}".format("||  S2 not find "+oFileFilter.mFileName))

    @staticmethod
    def check3SInSrc(oPatchModifyItem, target_git_dir):
        startlist=[]
        ostartobj=[]
        endlist=[]
        oendobj=[]

        try:
            oFileFilter = FileFilter(oPatchModifyItem.mOPatch.mFilename)
        except IOError:
            colorprint.err(oPatchModifyItem.mOPatch.mFilename+" isn't found")
            return

        colorprint.info("check patch item in "+ oFileFilter.mFileName)
        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        oCmpLine= oFileFilter.searchByWholeLine(patchItemTarg)
        if oCmpLine== "":
            colorprint.blue(oPatchModifyItem.mStartLine)
            #colorprint.err("ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")

        for i in range(1,4):
            if oPatchModifyItem.mPItemConList[i][-1] != "\n":
                startlist.append(oPatchModifyItem.mPItemConList[i][1:]+"\n")
            else:
                startlist.append(oPatchModifyItem.mPItemConList[i][1:])

            if oPatchModifyItem.mPItemConList[i][-1] != "\n":
                endlist.append(oPatchModifyItem.mPItemConList[i-4][1:]+"\n")
            else:
                endlist.append(oPatchModifyItem.mPItemConList[i-4][1:])

        print "3S:"
        patchMerge.check3Lines(startlist, oFileFilter.mFileName, "./")
        print "3E:"
        patchMerge.check3Lines(endlist, oFileFilter.mFileName, "./")

    @staticmethod
    def check3SInDstc(oPatchModifyItem, target_git_dir):
        startlist=[]
        ostartobj=[]
        endlist=[]
        oendobj=[]

        try:
            oFileFilter = FileFilter(target_git_dir+"/"+oPatchModifyItem.mOPatch.mFilename)
        except IOError:
            colorprint.err(oPatchModifyItem.mOPatch.mFilename+" isn't found")
            return

        colorprint.info("check patch item in "+ oFileFilter.mFileName)
        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        patchItemTarg = re.sub('^@.*@@\s', "", oPatchModifyItem.mPItemConList[0][1:])
        oCmpLine= oFileFilter.searchByWholeLine(patchItemTarg)
        if oCmpLine== "":
            colorprint.blue(oPatchModifyItem.mStartLine)
            colorprint.err("ERR:TAG:-->"+patchItemTarg+"<--NOT FIND")

        for i in range(1,4):
            if oPatchModifyItem.mPItemConList[i][-1] != "\n":
                startlist.append(oPatchModifyItem.mPItemConList[i][1:]+"\n")
            else:
                startlist.append(oPatchModifyItem.mPItemConList[i][1:])

            if oPatchModifyItem.mPItemConList[i][-1] != "\n":
                endlist.append(oPatchModifyItem.mPItemConList[i-4][1:]+"\n")
            else:
                endlist.append(oPatchModifyItem.mPItemConList[i-4][1:])

        patchMerge.check3Lines(startlist, oFileFilter.mFileName, "./")
        print "3E:"
        patchMerge.check3Lines(endlist, oFileFilter.mFileName, "./")

    @staticmethod
    def rmItem(oPatchModifyItem):
        "remove this patch item in patch"
        oPatchModifyItem.rmInPatch()

    @staticmethod
    def rePatchItem(oPatchModifyItem):
        "remove this patch item in patch"
        oPatchModifyItem.rePatchSrc()

    @staticmethod
    def mergeItem(oPatchModifyItem, target_git_dir):
        patchMerge.check3SInSrc(oPatchModifyItem, target_git_dir)
        patchMerge.check3SInDstc(oPatchModifyItem, target_git_dir)
        
        print ("what do you want to handle:")
        print "1. rm this item."
        print "2. replace the conflict lines"
        print "3. exit it"
        answer=raw_input("select: ")
        if answer == "1":
            patchMerge.rmItem(oPatchModifyItem);
        elif answer == "2":
            patchMerge.rePatchItem(oPatchModifyItem)
        elif answer == "3":
            print "you select 2"
        
