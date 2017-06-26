#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from pyme  import mfiles;
from optparse import OptionParser;
import re;
import os;

def generateCtagFiles(srcDir,outDir):
    "generate the files list base the *.o file"
    filelist=os.popen("find "+outDir+" -name \"*.o\"").readlines()
    tagFilelist=[]
    for line in filelist:
        isCommonFIle=0
        ret = re.sub(outDir,"",line)
        if ret:
            for item in commonSrcDir:
                res = re.match(item, ret)
                if res:
                    isCommonFIle=1
                    break;
        if isCommonFIle:
            isCommonFIle=0
        else:
            srcname=srcDir+"/"+ret[:-2]+'c';
            if os.path.exists(srcname):
                if os.path.isfile(srcname):
                    tagFilelist.append(srcDir+"/"+ret[:-2]+"c\n")
            srcname=srcDir+"/"+ret[:-2]+'h';
            if os.path.exists(srcname):
                if os.path.isfile(srcname):
                    tagFilelist.append(srcDir+"/"+ret[:-2]+"h\n")


    return tagFilelist

parser = OptionParser()
parser.add_option("-s", "--srcdir", action="store",type="string", default="", dest="srcDir",
                  help="src directory name", metavar="DERECTORY")

parser.add_option("-o", "--out",
                  action="store", type="string", dest="outDir", default="",
                  help="-m -f file", metavar="filename"
                  )
(options, args) = parser.parse_args()

#ctags -f linux_base-tags $TAG_ARGS $LINUX_SRC/drivers/base/
if options.srcDir=="":
    print "     err, not provide src dir"
    exit();

commonSrcDir=[
"drivers/base/",
"include/linux/",
"include/asm-generic/"
"kernel/",
"mm/",
"arch/arm/common/",
"arch/arm/kernel/",
"arch/arm/mm/"
]

if options.outDir!="":
    tagFiles = generateCtagFiles(options.srcDir, options.outDir)
else:
    tagFiles = generateCtagFiles(options.srcDir, options.srcDir)

for item in commonSrcDir:
    list=os.popen("find "+options.srcDir+"/"+item+" -name \"*.[chS]\"").readlines();
    tagFiles.extend(list)

for line in tagFiles:
    print line

cscopefile=options.srcDir+"/"+"cscope.files"
os.system("cd "+options.srcDir+"&& rm tags cscope.* -f")
f = open(cscopefile,"w+")
f.writelines(tagFiles)
f.close();
os.system("ctags -L cscope.files")
os.system("cscope -bkq -i cscope.files")
