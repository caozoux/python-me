#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import mfiles;
from pyme  import patchop;
from optparse import OptionParser;
import multiprocessing;
import colorprint;
import os;
import re;

opatch = []

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
                  help="-e -s file -d patchdir to find the existes patch in shortlog",
                  )

parser.add_option("-j", "--thread",
                  action="store", type="int", default="1", dest="threadsCount",
                  help="how many threads to run",
                  )

parser.add_option("-m", "--no-merge",
                  action="store_false", type="int", default=False, dest="noMerge",
                  help="how many threads to run",
                  )

parser.add_option("-m", "--formatpatch",
                  action="store_false", type="string", default="", dest="formatPatch",
                  help="-m commit -s shortlog -d patchOutDir, format one patch by commit, comment can be id or comment",
                  )

parser.add_option("-mx", "--commitlist",
                  action="store_false", type="string", default="", dest="commitlist",
                  help="-mx commitListFile -s shortlog -d patchOutDir, format patches by commitlist, comment can be id or comment",
                  )

(options, args) = parser.parse_args()

bufShortLog = open(options.shortlog).read()
if options.threadsCount > 1 and options.cmp:
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
    for itme in fileLines:
        print item

def threadSearch(buf, start, end):
    print "start: ", start, " end:", end
    for index in range(start,end):
        commit = patchop.patchFilter.getCommit(options.patchdir+opatch.filelist[index][:-1])
	print commit+ "patch:"+opatch.filelist[index][:-1]
        result = re.search(commit, buf);
        if result:
            colorprint.info(opatch.filelist[index][:-1])
            colorprint.info("find commit:  "+commit)
