#!/usr/bin/env python3

#from pyme  import mfiles
from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from pyme  import mfiles;
from optparse import OptionParser;
import re;
import os;

parser = OptionParser()
parser.add_option("-s", "--srcdir", action="store",type="string", default="", dest="srcDir",
                  help="src directory name", metavar="DERECTORY")

parser.add_option("-o", "--out",
                  action="store", type="string", dest="outDir", default="",
                  help="-m -f file", metavar="filename"
                  )
(options, args) = parser.parse_args()

if options.srcDir[-1] == "/":
    arg_srcDir=options.srcDir[:-1]
else:
    arg_srcDir=options.srcDir

if options.outDir[-1] == "/":
    arg_outDir=options.outDir[:-1]
else:
    arg_outDir=options.outDir
