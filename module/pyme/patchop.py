
from mfiles import *;
import os;
class patchFilter:
    def __init__(self, name):
        self.mPatchName = name

    @staticmethod
    def getCommit(patchname):
        ofile = FileFilter(patchname)
        ret = ofile.searchByLine("Subject.*$")
        commitStartLine = re.sub(r'Subject.*]\s',"", ret.mLine)
        commitEndLine=ofile.getLine(ret.mLineNumber+1)
        if commitEndLine[:4] == "MIME":
            return commitStartLine;
        else:
            return commitStartLine + commitEndLine;


class patchOperation:

    def __init__(self):
        pass;

    @staticmethod
    def patchOpApply(patchname, flag=1):
        "flag: \
            0: normal git apply \
            1: redirectory the error std to std io"
        if flag == 0:
            return os.popen("git apply "+patchname).readlines();
        elif flag == 1:
            return os.popen("git apply "+patchname+" 2>&1"+" | grep \"error: patch failed:\" ").readlines();

    @staticmethod
    def srcPatchList(gitsrc, filename, mode="oneline"):
        "it show all the patches of filename\
         mode: oneline \
               short   \
        "

        print gitsrc, filename
        if os.path.exists(gitsrc) and os.path.exists(filename):
            pass
        else:
            #return ""
            pass

        if mode == "oneline":
            listPatchBuf = os.popen("git -C "+gitsrc+ " log --no-merges --pretty=oneline "+filename+" |  cut -d ' ' -f 2-").readlines()
            print "git -C "+gitsrc+ " log --pretty=oneline | cut -d ' ' -f 2-"
            if len(listPatchBuf):
                return listPatchBuf

        elif mode == "short":
            listPatchBuf = os.popen("git -C "+gitsrc+ " log --pretty=short | cut -d \" \" -f 2-"+filename).readlines()
            if len(listPatchBuf):
                return listPatchBuf
        else:
            return ""
        return ""

    @staticmethod
    def patchFormatCmit(gitsrc, commit, shorLogBuf):
        pass

    @staticmethod
    def patchFormatId(gitsrc, id, shorLogBuf):
        pass
