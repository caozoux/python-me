#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import mfiles;
from pyme  import patchop;
from optparse import OptionParser;
from patch import patchbase;
import multiprocessing;
import colorprint;
import os;
import re;

opatch = []

def threadSearch(buf, start, end):
    print "start: ", start, " end:", end
    for index in range(start,end):
        commit = patchop.patchFilter.getCommit(options.patchdir+opatch.filelist[index][:-1])
        #commit=commit.replace("(","\(").replace(")","\)").replace(".", "\.").replace("[", "\[").replace("]", "\]")
        commit= re.escape(commit)
	print commit+ "patch:"+opatch.filelist[index][:-1]
        print opatch.filelist[index][:-1]+" commit:{"+commit[:-1]+"}"
        result = re.search(commit, buf);
        if result:
            colorprint.info(" find "+opatch.filelist[index][:-1]+": "+commit[:-1]+":")
            print("  findpatch:  "+opatch.filelist[index][:-1])

parser = OptionParser()

parser.add_option("-j", "--thread",
                  action="store", type="int", default="1", dest="threadsCount",
                  help="how many threads to run",
                  )

parser.add_option("-s", "--shortlog",
                  action="store", type="string", dest="shortlog",
                  help="[-e -j N -s * -d *, shortlog file name, it is used to comparet with patches",
                  metavar="gitLogFile")
parser.add_option("-d", "--patchdir",
                  action="store", type="string", dest="patchdir",
                  help="-e -j N -s * -d *, patches directory patch",
                  metavar="patchDirc")

parser.add_option("-e", "--getinsortlog",
                  action="store_true",  dest="cmp",
                  help="-j2 -e -s file -d patchdir to find the existes patch in shortlog",
                  )

parser.add_option("--fm", "--formatpatch",
                  action="store", type="string", default="", dest="formatPatch",
                  help="-m commit -s shortlog -d patchOutDir, format one patch by commit, comment can be id or comment",
                  )

parser.add_option("--mx", "--commitlist",
                  action="store", type="string", default="", dest="commitlist",
                  help="-mx commitListFile -s shortlog -d patchOutDir, format patches by commitlist, comment can be id or comment",
                  )

parser.add_option("--ck", "--checktargetfile",
                  action="store", type="string", default="", dest="checktargetfile",
                  help="--ck $targetlist(it is *.o files list), check the target is exist in current prj",
                  )

parser.add_option("--gt", "--getfilesfrompatches",
                  action="store", type="string", default="", dest="getfilesfrompatches",
                  help="--gt $patchdir $outdir, get the modified files by patches, then check the *.c is exists in $outdir"
                  )

(options, args) = parser.parse_args()

if options.threadsCount > 0 and options.cmp:
    bufShortLog = open(options.shortlog).read()
    opatch = mfiles.fileDirList(options.patchdir)

    if (options.patchdir[-1:] == "/"):
        pass
    else:
        options.patchdir += "/"

    listlen = len(opatch.filelist)
    size = listlen/options.threadsCount
    pool = multiprocessing.Pool(processes=options.threadsCount)
    result=[]

    print size
    for i in range(options.threadsCount):
        print i
        if (i+1)*size > listlen:
            result.append(pool.apply_async(threadSearch, (bufShortLog, i*size, listlen)))
        else:
            result.append(pool.apply_async(threadSearch, (bufShortLog, i*size,  (i+1)*size)))
    pool.close()
    pool.join()

    for res in result:
        print res.get()

if options.commitlist:
    if os.path.exists(options.shortlog):
        if os.path.exists(options.patchdir):
            pass
        else:
            os.system("mkdir -p "+options.patchdir)
    else:
         colorprint.err("err: not find "+options.shortlog)
         exit(1)

    fileLines = open(options.commitlist).readlines()
    size = len(fileLines)
    for number in range(size):
        os.system("git format-patch --start-number "+str(size-number)+" -1 "+fileLines[number][:-1]+" -o "+options.patchdir)



if options.checktargetfile:
    if os.path.exists(options.checktargetfile):
        lines = open(options.checktargetfile).readlines()
        for line in lines:
            filename=line[:-2]+"c"
            if os.path.exists(filename):
                print filename, " is exist"
            else:
                print filename, " is not exist"

if options.getfilesfrompatches:
    patches = os.popen("ls "+options.getfilesfrompatches).readlines()
    for line in patches:
        patchname = options.getfilesfrompatches+"/"+line[:-1]
        files=patchbase.PatchBase.getFilesFromPatch(patchname)

        cfiles_cnt=0
        chead_cnt=0
        others_cnt=0
        cfiles_nobuilt_cnt=0
        dts_cnt=0

        for file in files:
            if file[-2:] == ".c":
                cfiles_cnt += 1
                if os.path.exists(file[:-2]+ ".o"):
                    print patchname, file[:-2]+".o", " is built"
                    break;
                else:
                    cfiles_nobuilt_cnt += 1
                    print patchname, file, " is not built"
            elif file[-2:] == ".h":
                chead_cnt += 1
            elif file[-4:] == ".dts":
                dts_cnt += 1
            elif file[-5:] == ".dtsi":
                dts_cnt += 1
            else:
                others_cnt += 1
        if cfiles_cnt > 0:
            if cfiles_cnt == cfiles_nobuilt_cnt:
                print "note: ", patchname, " maybe can remove"
        else:
            if dts_cnt == 0:
                if chead_cnt > 0:
                    print "note: ", patchname, " just have head file"
                else:
                    print "note: ", patchname, " just have other file"
