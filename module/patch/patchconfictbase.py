#!/usr/bin/env python2.7
import re
import sys
import os
import patchbase
from clrpr import clrprt

class FileOp(object):

    """Docstring for FileOp. """
    def __init__(self):
        """TODO: to be defined1. """
    @staticmethod
    def getSpecifyLine(file, linenumber):
        """get specify line from file """
        filebuflist=open(file).readlines()
        return filebuflist[linenumber-1]

#conflict_filename: error: patch failed: drivers/tty/serial/sh-sci.c:84
class PatchConflictItem(object):
    """Docstring for PatchConflictItem. """
    def __init__(self, patchname, patchConflictInfor):
        self.patchname = patchname
        """TODO: to be defined1. """
        res=re.search(": .*:[0-9]", patchConflictInfor)
        conflict_filenmae = res.group(0)[16:-2]
        res=re.search(":[0-9]*\n", patchConflictInfor)
        if res:
            conflictnumber= res.group(0)[1:-1]
            listbuf=patchbase.PatchBase.getPatchModifiedItemByConflictNumber(self.patchname, int(conflictnumber), conflict_filenmae)
        else:
            return

        #self.patchitem_head @@ -84,6 +84,7 @@ struct sci_port {
        self.conflictFile =conflict_filenmae
        self.patchitem_head = listbuf[0]
        self.patchitem_head_buf = listbuf[0]
        self.patchitem_start = listbuf[1:4]
        self.patchitem_start_buf = "".join(listbuf[1:4])
        self.patchitem_start_buf=re.sub("\n ", "\n", self.patchitem_start_buf[1:])
        self.patchitem_end = listbuf[-3:]
        self.patchitem_end_buf = "".join(listbuf[-3:])
        self.patchitem_end_buf =re.sub("\n ", "\n", self.patchitem_end_buf[1:])
        self.patchitem_context = listbuf[4:-3]
        self.patchitem_context_buf = "".join(listbuf[4:-3])
        self.patchitem_context_buf = re.sub("\n ", "\n", self.patchitem_context_buf[1:])
        #self.patchitem_start struct sci_port {
        self.patchitem_head_start = re.sub("\@\@.*\@\@ ", "", self.patchitem_head_buf)

    def patchItemContextType(self):
        """TODO: Docstring for patchItemContextType.
        :returns: 0: all add, 1: all del, 2: del and ad
        """
        cnt_add=0
        cnt_del=0
        for line in self.patchitem_context:
            if line[0] == "+":
                cnt_add += 1
            elif line[0] == "-":
                cnt_del -= 1
        if cnt_add > 0:
            if cnt_del == 0:
                return 0
            else:
                return 2
        return 1

    def getStartLine(self, filename, linebufs):
        """get the line number where the linebufs in file
        :args: linebufs is multiple lines
        :returns: the line number in conflictFile

        """
        filebuf = open(filename).read()
        ret =filebuf.find("\n"+self.patchitem_head_start)
        if ret >= 0:
            startcnt= ret
        else:
            startcnt = 0

        findcnt = filebuf[startcnt:].find(linebufs)
        ret = filebuf[(startcnt+findcnt+1):].find(linebufs)
        if ret == -1:
            cnt=filebuf[:(startcnt+findcnt)].count("\n")+1
            return cnt
        else:
            print "there are multiple places for:"
            print linebufs
            return -2
        return -1

class PatchConflictBase(object):

    """Docstring for PatchConflictBase. """

    def __init__(self, patchname):
        """TODO: to be defined1. """
        self.patchname = patchname

    def showConflictPlace(self, conflictline):
        res=re.search(": .*:[0-9]", conflictline)
        conflict_filenmae = res.group(0)[16:-2]
        res=re.search(":[0-9]*\n", conflictline)
        if res:
            conflictnumber= res.group(0)[1:-1]
            listbuf=patchbase.PatchBase.getPatchModifiedItemByConflictNumber(self.patchname, int(conflictnumber), conflict_filenmae)
        else:
            return
        patchitem_head = listbuf[0]
        patchitem_head_buf = listbuf[0]
        patchitem_start = listbuf[1:4]
        patchitem_start_buf = "".join(listbuf[1:4])
        patchitem_start_buf=re.sub("\n ", "\n", patchitem_start_buf[1:])
        patchitem_end = listbuf[-3:]
        patchitem_end_buf = "".join(listbuf[-3:])
        patchitem_end_buf=re.sub("\n ", "\n", patchitem_end_buf[1:])
        patchitem_context = listbuf[4:-3]
        patchitem_context_buf = "".join(listbuf[4:-3])
        patchitem_context_buf =re.sub("\n ", "\n", patchitem_context_buf[1:])
        patchitem_head_start = re.sub("\@\@.*\@\@ ", "", patchitem_head_buf)
        #print patchitem_head
        #print patchitem_head_start
        #print patchitem_start
        #print patchitem_end
        #print patchitem_context

        srcfilebuf= open(conflict_filenmae).read()
        srcfilebuflines= open(conflict_filenmae).readlines()
        try:
            start_number=srcfilebuflines.index(patchitem_head_start)
        except Exception as e:
            print "not find:", conflict_filenmae, patchitem_head,

        ret=srcfilebuf.find(patchitem_start_buf)
        if ret>=0:
            clrprt.info(patchitem_start_buf[:-1])
        else:
            clrprt.err(patchitem_start_buf[:-1])
        print patchitem_context_buf

        ret=srcfilebuf.find(patchitem_end_buf)
        if ret>=0:
            clrprt.info(patchitem_end_buf[:-1])
        else:
            clrprt.err(patchitem_end_buf[:-1])


    def getPatchItemByConflictline(self, conflictline):
        "get patchitem by like error: patch failed: sound/soc/sh/rcar/dma.c:494"

        res=re.search(": .*:[0-9]", conflictline)
        conflict_filenmae = res.group(0)[16:-2]
        res=re.search(":[0-9]*\n", conflictline)
        if res:
            conflictnumber= res.group(0)[1:-1]
            listbuf=patchbase.PatchBase.getPatchModifiedItemByConflictNumber(self.patchname, int(conflictnumber), conflict_filenmae)
            print "patchitem head:", listbuf[0]
            print "patchitem 3sline:", listbuf[1:4]
            print "patchitem 3eline:", listbuf[-3:-1]
        return listbuf;

    def getConfilictList(self, remote=""):
        """get the patch conflict list
        :returns: TODO

        """
        gitapplybuf=os.popen("git apply "+self.patchname+" 2>&1"+" | grep \"error: patch failed:\" ").readlines();
        return gitapplybuf

if __name__ == "__main__":
    obj = PatchConflictBase(sys.argv[1])
    for line in obj.getConfilictList():
        patchConflictITem= PatchConflictItem(sys.argv[1], line)
        ret = patchConflictITem.patchItemContextType()
        if ret == 0:
            #the conflict patch is all add lines
            print "all add"
            ret = patchConflictITem.getStartLine(patchConflictITem.conflictFile,  patchConflictITem.patchitem_start_buf)
            if ret >=0:
                #we find the patch start, so the endline isn't found
                print "find the patchitem start:"
                print "%-70s"%patchConflictITem.conflictFile
                print "%-70s"%patchConflictITem.patchitem_head[:-1],
                print "%-70s"%("srcFile:"+patchConflictITem.conflictFile+": "+str(ret))


                print "%-70s"%patchConflictITem.patchitem_start[0][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret))[:-1]
                print "%-70s"%patchConflictITem.patchitem_start[1][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret+1))[:-1]
                print "%-70s"%patchConflictITem.patchitem_start[2][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret+2))[:-1]

                for line in patchConflictITem.patchitem_context:
                    print line.replace("\t","^")[:-1]

                print "%-70s"%patchConflictITem.patchitem_end[0][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret+3))[:-1]
                print "%-70s"%patchConflictITem.patchitem_end[1][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret+4))[:-1]
                print "%-70s"%patchConflictITem.patchitem_end[2][:-1].replace("\t","^"),"=",
                print "%-70s"%FileOp.getSpecifyLine(patchConflictITem.conflictFile, int(ret+5))[:-1]

                startnum=ret+3
                addlines=[]
                for line in patchConflictITem.patchitem_context:
                    print line.replace("\t","^")[:-1]
                    if line[0] == "+":
                        addlines.append(line)
                    else:
                        answer=raw_input("do you want insert(y/n):")
                        if answer == "y":
                            for insertline in addlines:
                                #os.system("sed -i "+str(startnum)+" "+insertline[:-1]+" "+patchConflictITem.conflictFile)
                                print("sed -i "+str(startnum)+" "+insertline[:-1]+" "+patchConflictITem.conflictFile)
                            addlines=[]
                if len(addlines) > 0:
                        answer=raw_input("do you want insert(y/n):")
                        if answer == "y":
                            for insertline in addlines:
                                #os.system("sed -i "+str(startnum)+" "+insertline[:-1]+" "+patchConflictITem.conflictFile)
                                print("sed -i \""+str(startnum)+" "+insertline[1:-1]+"\" "+patchConflictITem.conflictFile)


        elif ret == 1:
            print "all del"
        else:
            print "add del"

