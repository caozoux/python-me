#!/usr/bin/env python2.7
from mfiles import *;

class patchMerge:
    def __init__(self,opatchitem,srcfilename):
        self.mOPatchItem = opatchitem
        self.mSrcFile = srcfilename
        #SFULL SMIDLE $LOW
        self.mModeStart=""

    def mergeItem(self,srcstart,patchstart):
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
                    self.mModeStart="SFULL"
                    pass;
            elif ostartobj[2].mLineNumber - ostartobj[1].mLineNumber == 1:
                self.mCmpStartline = ostartobj[2].mLineNumber-2
                self.mModeStart="SMIDLE"
                pass
            else:
                print "can't find start three lines"
                return

        elif len(ostartobj) == 2:
            if ostartobj[1].mLineNumber - ostartobj[0].mLineNumber == 1:
                self.mModeStart="SMIDLE"
        else:
                print "can't find start three lines"
                return

