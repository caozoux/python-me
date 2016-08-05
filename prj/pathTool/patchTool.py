#!/usr/bin/env python2.7

#from pyme  import mfiles
from pyme  import mfiles;
from pyme  import patchop;
from optparse import OptionParser;
import re;
import multiprocessing;

opatch = []
def threadSearch(buf, start, end):
    print "start: ", start, " end:", end
    for index in range(start,end):
        commit = patchop.patchFilter.getCommit("/home/zoucao/github/linux-stable/patches/"+opatch.filelist[index][:-1])
        result = re.search(commit, buf);
        if result:
            print "find commit:  "+commit;

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-s", "--shortlog",
                  action="store", type="string", dest="shortlog",
                  help="shortlog file name, it is used to comparet with patches",
                  metavar="filename")
parser.add_option("-d", "--patchdir",
                  action="store", type="string", dest="patchdir",
                  help="patches directory patch",
                  metavar="filename")

parser.add_option("-e", "--getinsortlog",
                  action="store_true",  dest="cmp",
                  help="-e -s file -d patchdir to find the existes patch in shortlog",
                  )
parser.add_option("-j", "--thread",
                  action="store", type="int", default="1", dest="threadsCount",
                  help="how many threads to run",
                  )

(options, args) = parser.parse_args()

bufShortLog = open(options.shortlog).read()
if options.threadsCount > 1:
    opatch = mfiles.fileDirList(options.patchdir)
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

