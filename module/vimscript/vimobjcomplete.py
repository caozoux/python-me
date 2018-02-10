import os
import re

#class ObjCompleteNote;
#class ObjCompleteLayer;
#class ObjCompleteHead; 
#class ObjCompleteManger; 

class ObjCompleteHead(object):
    def __init__(self, filename, head, manager_obj):
        self.filename= filename
        self.headline=head;
        self.head=self.headline.split('\t')[0]
        self.m_manager = manager_obj
        #self.headnote=self.headline.split('\t')[1]
    def dump(self):
        """TODO: Docstring for dump.
        :returns: TODO
        """
        print self.head 
        ret =  self.m_manager.getExtern(self.head)
        if ret:
            print "extern:"
            print ret


class ObjCompleteManger(object):
    def __init__(self, filename, externfilename):
        self.filename = filename
        #file lines list
        self.listlines=[]
        #ObjCompleteHead obj list
        self.headObjList = []
        #very head in self.listlines
        self.headlist= []
        #extern buf
        self.externfilename = externfilename

    def transferToHead(self):
        self.externlistlines = open(self.externfilename).readlines()
        self.listlines= open(self.filename).readlines()
        self.filebuf= open(self.filename).read()
        self.externfilebuf= open(self.externfilename).read()
        for line in self.listlines:
            obj = ObjCompleteHead(self.filename, line, self)
            head=line.split('\t')[0]
            self.headlist.append(head)
            self.headObjList.append(obj)

    def getExtern(self, head):
        externlist=""
        res = re.search("\n"+head+"\W*\n", self.externfilebuf)
        off=0;
        end=0;
        if res:
            off=self.externfilebuf.find(res.group(0))
            if off < 0:
                return ""
            off += len(res.group(0))
            res=re.search("\n\w", self.externfilebuf[off:])
            if res:
                end=self.externfilebuf[off:].find(res.group(0))
                externlist = self.externfilebuf[off:(end+off)]

        return externlist

    def dump(self):
        for obj in self.headObjList:
            obj.dump()
