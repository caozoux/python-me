import os
import re

class MeBaseGit(object):
    def __init__(self, configFile=" ~/.megitpython"):
        self.oEnvFile=configFile

    def _CoverStrPartarn(self, string):
        return string.replace("\"","\\\"")

    def _ReadPatch(self, patch):
        fd =open(patch, 'r')
        buf = fd.read()
        fd.close()
        return buf;

    def _FindPatch(self, patch, gitdir):
        title = self.GitCommitHead(patch)
        paternstring=self._CoverStrPartarn(title)
        #cmd="cd "+gitdir+"; git log  --pretty=oneline  --grep=\""+paternstring+"\""+" --all-match"
        cmd="cd "+gitdir+"; git log  --pretty=oneline  --grep=\""+paternstring+"\""
        ret=os.popen(cmd).readlines()
        print(len(ret))

    #find a list of patches in gittree
    def _FindPatches(self, patches, gitdir):
        titlelist=[]
        for patch in patches:
            title = self.GitCommitHead(patch)
            if title:
                paternstring=self._CoverStrPartarn(title)
                titlelist.append(" --grep=\"" +paternstring+"\" ")

          
        #cmd="cd "+gitdir+"; git log  --pretty=oneline  --grep=\""+paternstring+"\""+" --all-match"
        #cmd="cd "+gitdir+"; git log  --pretty=oneline  --grep=\""+paternstring+"\""
        #ret=os.popen(cmd).readlines()
        #print(len(ret))

    def GitAuthor(self, patch):
        buf=self._ReadPatch(patch)
        res=re.search("From:.*", buf)
        if res:
            author=res.group()
            author=author.replace("From: ","")
            return author
        return ""

    def GitCommitHead(self, patch):
        buf=self._ReadPatch(patch)
        res=re.search("Subject: \[.*", buf)
        if res:
            title=res.group()
            res=re.sub("Subject.*] +", "", title)
            if res:
                return res
        return ""

    def GitCommitContext(self, patch):
        buf=self._ReadPatch(patch)
        res=re.search("\n\n.*?---", buf, flags=re.DOTALL)
        if res:
            return res.group()[2:-3]

    def CheckMainline(self, patch):
        pass 

    def FormatPatchFromMainline(self, patch):
        pass 

    def CheckPatchForamt(self, patch):
        pass 

    def CheckPatchIsInGit(self, patch, gitdir):
        author = self.GitAuthor(patch)
        title = self.GitCommitHead(patch)
        context = self.GitCommitContext(patch)
        self._FindPatch(patch,gitdir)

    def CheckPatceshIsInGit(self, patchdir, gitdir):
        author = self.GitAuthor(patch)
        title = self.GitCommitHead(patch)
        context = self.GitCommitContext(patch)
        self._FindPatch(patch,gitdir)

TestPatch="./0001-arm64-mm-add-p-d_leaf-definitions.patch"
if __name__ == "__main__":
    oGitBase=MeBaseGit()
    oGitBase.CheckPatchIsInGit(TestPatch, "/home/zc/github/linux_mailine")
    #print("author:", oGitBase.GitAuthor(TestPatch))
    print("title:", oGitBase.GitCommitHead(TestPatch))
    #print("context:\n"+str(oGitBase.GitCommitContext(TestPatch)))

