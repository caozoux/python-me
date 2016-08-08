#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from optparse import OptionParser;
import re;

parser = OptionParser()
parser.add_option("-f", "--patch", dest="patchname",
                  help="assnig patch name", metavar="FILE")
parser.add_option("-m", "--merge",
                  action="store_true",  dest="opMerge",
                  help="-m -f file",
                  )
(options, args) = parser.parse_args()

#commit = patchop.patchFilter.getCommit("/home/zoucao/github/linux-stable/patches/"+opatch.filelist[index][:-1])
patchname=args[0]
list = patchop.patchOperation.patchOpApply(patchname, flag=1)
oPatchContext = patchcontext.patchcontext(patchname)
oPatchContext.analysis()

for line in list:
    print line;
    var = re.sub("error: patch failed:.*:", "", line)
    var = var[:-1]
    oPatchModifyItem = oPatchContext.findPatchItemByLine(var)
    #oPatchModifyItem.dump()
    oPatchModifyItem.showSrcAndItem()
    oPatchModifyItem.mergeItem(oPatchModifyItem.mCmpStartline,0)
    oMerge = patchMerge(oPatchModifyItem, oPatchModifyItem.mCmpStartline)

