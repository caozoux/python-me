
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

