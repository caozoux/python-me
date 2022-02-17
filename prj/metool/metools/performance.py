import os
import re
from API import api
from optparse import OptionParser


sysbenchpre={
"fileio": "./src/sysbench fileio --file-total-size=5G --file-test-mode=rndrw --time=30 prepare",
"mysql": "./src/sysbench --mysql-host=127.0.0.1 --mysql-port=3306  --mysql-user=root --mysql-password='123456' --mysql-db=testdb --db-driver=mysql --tables=10 --table-size=500000  --report-interval=10 ./src/lua/oltp_insert.lua prepare",
}

sysbenchrun={
"cpu":"./src/sysbench cpu --cpu-max-prime=20000 run",
"fileio": "./src/sysbench fileio --file-total-size=5G --file-test-mode=rndrw --time=30 run",
"mutex": "./src/sysbench mutex --mutex-num=4096 --mutex-locks=50000 --mutex-loops=10000 run",
"threads": "./src/sysbench threads --thread-yields=1000 --thread-locks=8 run",
"memory": "./src/sysbench memory  run",
"mysql": "./src/sysbench --mysql-host=127.0.0.1 --mysql-port=3306  --mysql-user=root --mysql-password='123456' --mysql-db=testdb --db-driver=mysql --tables=10 --table-size=500000  --report-interval=10 ./src/lua/oltp_insert.lua run",
}

sysbenchclean={
"fileio": "./src/sysbench fileio --file-total-size=5G --file-test-mode=rndrw --time=30 cleanup",
"mysql": "./src/sysbench --mysql-host=127.0.0.1 --mysql-port=3306  --mysql-user=root --mysql-password='123456' --mysql-db=testdb --db-driver=mysql --tables=10 --table-size=500000  --report-interval=10 ./src/lua/oltp_insert.lua cleanup",
}

def CaseSysbenchBaseResult(context, numbers):
    jsdict={}
    lines=context.split("\n")
    for index in numbers:
        res=re.sub(' +', ' ', lines[index]).strip().split(":")
        jsdict[res[0]]=res[1]
    print(jsdict)

def CaseSysbenchFileioResult(context):
    return CaseSysbenchBaseResult(context,[23,24,25])

def CaseSysbenchThreadsResult(context):
    return CaseSysbenchBaseResult(context,[13])

def CaseSysbenchMemoryResult(context):
    return CaseSysbenchBaseResult(context,[23])

def CaseSysbenchMutexResult(context):
    return CaseSysbenchBaseResult(context,[13,19])

def CaseSysbenchCpuResult(context):
    return CaseSysbenchBaseResult(context,[14,26])

def CaseSysbenchMysqlResult(context):
    return CaseSysbenchBaseResult(context,[18])

sysbenchresult={
"cpu": CaseSysbenchCpuResult,
"fileio": CaseSysbenchFileioResult,
"mutex": CaseSysbenchMutexResult,
"threads": CaseSysbenchThreadsResult,
"memory": CaseSysbenchMemoryResult,
"mysql": CaseSysbenchMysqlResult,
}

benchmark={
"sysbench":"https://github.com/akopytov/sysbench/archive/master.zip",
"unixbench":"https://github.com/kdlucas/byte-unixbench/archive/refs/heads/master.zip",
"wrk": "https://github.com/wg/wrk/archive/refs/heads/master.zip",
"ltp": "https://github.com/HIT-SCIR/ltp/archive/refs/heads/master.zip",
"netperf": "https://github.com/HewlettPackard/netperf/archive/refs/heads/master.zip"
}


def RunSysbench(name, workdir):
    res=""
    if sysbenchpre.get(name):
        #api.excuteCommand(workdir+sysbenchpre[name], 1, 1)
        api.excuteCommand("cd "+workdir+";"+sysbenchpre[name], 1, 1)
    if sysbenchrun.get(name):
        res=api.excuteCommand("cd "+workdir+";"+sysbenchrun[name], 1, 1)
        #print(res)
        api.dumpline(res)
    if sysbenchclean.get(name):
        #api.excuteCommand(workdir+sysbenchclean[name], 1, 1)
        api.excuteCommand("cd "+workdir+";"+sysbenchclean[name], 1, 1)

    if sysbenchresult.get(name):
        sysbenchresult[name](res)


def RunSimpleBench(name, subname):
    if name == "sysbench":
        RunSysbench(subname, "work/sysbench-master/")

def BuildSimpleBench(name):
    """TODO: Docstring for BuildSimpleBench.
    :returns: TODO

    """

    return api.excuteCommand(". ./script/build/"+name+"__build.sh ", 0, 1)

def InstallSimpleBench(name):
    if not os.path.exists("work"):
        os.mkdir("work")
    if benchmark[name]:
        #res=api.excuteCommand("wget "+benchmark[name]+ " -O work/"+name+".zip", 0, 1)
        #if res:
        #    printf("wget ",name, "download error")
        res=api.excuteCommand("unzip -o -xd ./work ./work/"+name+".zip", 0, 1)
        #res=api.excuteCommand("./script/build/"+name+"__build.sh", 0, 1)
        BuildSimpleBench(name)

def BenchmarkInstall(name):
    if name == "all":
        pass
    else:
        InstallSimpleBench(name)

parser = OptionParser()
parser.add_option("-i", "--install", type="string", dest="install",
                  help="--install  all/sysbench/unixbench/hackbench/wrk/niginx/radis/cpuspec")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run all/sysbench/unixbench/hackbench/wrk/niginx/radis/cpuspec")
parser.add_option("-c", "--case", type="string", dest="case",
                  help="--case all/sysbench/unixbench/hackbench/wrk/niginx/radis/cpuspec")

(options, args) = parser.parse_args()

if options.install:
    BenchmarkInstall(options.install)
if options.run and options.case:
    RunSimpleBench(options.run, options.case)
if options.list:
    for key in benchmark:
        print(key, benchmark[key])
