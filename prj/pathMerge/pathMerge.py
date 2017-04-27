#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from optparse import OptionParser;
import colorprint
import re;
import os;


parser = OptionParser()
parser.add_option("-f", "--patch", dest="patchname",
                  help="assnig patch name", metavar="FILE")
parser.add_option("-m", "--merge",
                  action="store_true",  dest="opMerge",
                  help="-m -f file",
                  )
parser.add_option("-a", "--analysis",
                  action="store_true",  dest="showConflict",
                  help="-a -f $patch $lines, conflict start",
                  )
(options, args) = parser.parse_args()

if options.opMerge:
    if os.path.exists(options.patchname):
        pass
    else:
        colorprint.err("err: "+options.patchname+" not exist")
        exit(1)
    patchname = options.patchname
#commit = patchop.patchFilter.getCommit("/home/zoucao/github/linux-stable/patches/"+opatch.filelist[index][:-1])
    list = patchop.patchOperation.patchOpApply(patchname, flag=1)
    oPatchContext = patchcontext.patchcontext(patchname)
    oPatchContext.analysis()
    oPatchContext.dump()

    #print list
    for line in list:
        print "patch conflict "+line
        var = re.sub("error: patch failed:.*:", "", line)
        var = var[:-1]
        oPatchModifyItem = oPatchContext.findPatchItemByLine(var)
        if oPatchModifyItem:
            oPatchModifyItem.dump_patch()
        else:
            colorprint.err("patch item not find: "+line)

        #oPatchModifyItem.showSrcAndItem()
        #oPatchModifyItem.mergeItem(oPatchModifyItem.mCmpStartline,0)
        #oMerge = patchMerge(oPatchModifyItem, oPatchModifyItem.mCmpStartline)

if options.showConflict:
    if os.path.exists(options.patchname):
        pass
    else:
        colorprint.err("err: "+options.patchname+" not exist")
        exit(1)
    patchname = options.patchname
    oPatchContext = patchcontext.patchcontext(patchname)
    oPatchContext.analysis()
    oPatchContext.dump_patch()

    print patchname
    list = patchop.patchOperation.patchOpApply(patchname, flag=1)
    for line in list:
        print "patch conflict "+line
        var = re.sub("error: patch failed:.*:", "", line)
        var = var[:-1]
        oPatchModifyItem = oPatchContext.findPatchItemByLine(var)
        if oPatchModifyItem:
            oPatchModifyItem.dump_patch()
            oPatchModifyItem.checkAddline("/export/disk1T/bsp_work/xilinx-zynq/linux-xlnx")
            #oPatchModifyItem.mergeItem(oPatchModifyItem.mCmpStartline,0)
        else:
            colorprint.err("patch item not find: "+line)
        patchMerge.patchMerge.mergeItem(oPatchModifyItem, "/export/disk1T/bsp_work/xilinx-zynq/linux-xlnx")

