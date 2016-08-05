
from mfiles import *;
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

