#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import patchop;
from pyme  import patchcontext;
from pyme  import patchMerge;
from pyme  import mfiles;
from optparse import OptionParser;
import re;
import os;

archArm=[
"arch/arm/common",
"arch/arm/kernel",
"arch/arm/mm/"
]

commonSrcDir=[
"drivers/base",
"drivers/of",
"include/linux",
"include/asm-generic",
"kernel",
"mm",
"init",
]

def generateFindArgs(srcDir, outDir, ignore_dirs):
    " the shell command line by *.o but ignore the *.o in ignore_dirs"
    flags_first=0
    find_ignore_path_args="-type d \\( -path "
    for objs in ignore_dirs:
        if flags_first == 0:
            flags_first = 1
            find_ignore_path_args = find_ignore_path_args+" \""+outDir+"/"+objs+"\" "
        else:
            find_ignore_path_args = find_ignore_path_args+" -o -path \""+outDir+"/"+objs+"\" "
    find_ignore_path_args = find_ignore_path_args+" \) -prune -o -name \"*.o\" -print"
    res="find "+outDir+" "+find_ignore_path_args
    return res 

def generatSrcFilesByObjs(srcDir, outDir, Objlist):
    """ transfer objlist into file[.ch]
        outDir: build out Dir
        srcDir: source Dir
        Objlist:  obj file list
    """
    tagFilelist=[]
    for line in Objlist:
        ret = re.sub(outDir,"",line)
        if ret == "":
            continue

        srcname=srcDir+"/"+ret[:-2]+'c';
        if os.path.exists(srcname):
            if os.path.isfile(srcname):
                tagFilelist.append(srcDir+ret[:-2]+"c\n")
        srcname=srcDir+"/"+ret[:-2]+'h';
        if os.path.exists(srcname):
            if os.path.isfile(srcname):
                tagFilelist.append(srcDir+ret[:-2]+"h\n")
    return tagFilelist

def generateTargetFiles(srcDir, targeDir):
    """
        generate file list by targetDir, it will merge all files in
        targeDir into file list
    """
    tagFiles=[]
    for obj in targeDir:
        filelist=os.popen("find "+obj+" -name \"*.[ch]\"").readlines()
        tagFiles.extend(filelist)

    return tagFiles

def generateCtagFilesV2(srcDir,outDir, targeDir):
    """ src: source code
        outDir:  build out dir, it is used for generating the tag file list
        targetDir: it is used for ignoring the files from tag file.
    """

    allFilelist=[]
    objFilelist=[]
    tagFilelist=[]
    # here get the the file list with ignoring the targeDir
    findcmd=generateFindArgs(srcDir, outDir, targeDir)
    print findcmd
    filelist=os.popen(findcmd).readlines()
    objFilelist = generatSrcFilesByObjs(srcDir, outDir, filelist)
    #print objFilelist
    tagFilelist = generateTargetFiles(srcDir, targeDir)
    allFilelist.extend(objFilelist)
    allFilelist.extend(tagFilelist)
    #print allFilelist

    return allFilelist

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

if options.srcDir[-1] == "/":
    arg_srcDir=options.srcDir[:-1]
else:
    arg_srcDir=options.srcDir

if options.outDir[-1] == "/":
    arg_outDir=options.outDir[:-1]
else:
    arg_outDir=options.outDir

cscopefile=options.srcDir+"/"+"cscope.files"
tagFiles = generateCtagFilesV2(arg_srcDir, arg_outDir, commonSrcDir)
f = open(cscopefile,"w+")
f.writelines(tagFiles)
f.close();
os.system("ctags -L cscope.files")
os.system("cscope -bkq -i cscope.files")
