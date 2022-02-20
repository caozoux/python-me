import os
import re
import json
import time
from API import api
from optparse import OptionParser

benchmark={
"sysbench":"https://github.com/akopytov/sysbench/archive/master.zip",
"unixbench":"https://github.com/kdlucas/byte-unixbench/archive/refs/heads/master.zip",
"wrk": "https://github.com/wg/wrk/archive/refs/heads/master.zip",
"ltp": "https://github.com/HIT-SCIR/ltp/archive/refs/heads/master.zip",
"netperf": "https://github.com/HewlettPackard/netperf/archive/refs/heads/master.zip"
}

sysbenchpre={
"fileio": "./src/sysbench fileio --file-total-size=5G --file-test-mode=rndrw --time=30 prepare",
#"mysql": "./src/sysbench --mysql-host=127.0.0.1 --mysql-port=3306  --mysql-user=root --mysql-password='123456' --mysql-db=testdb --db-driver=mysql --tables=10 --table-size=500000  --report-interval=10 ./src/lua/oltp_insert.lua prepare",
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
#"mysql": "./src/sysbench --mysql-host=127.0.0.1 --mysql-port=3306  --mysql-user=root --mysql-password='123456' --mysql-db=testdb --db-driver=mysql --tables=10 --table-size=500000  --report-interval=10 ./src/lua/oltp_insert.lua cleanup",
}

def CaseSysbenchBaseResult(context, numbers, name):
    jsdict={}
    lines=context.split("\n")
    for index in numbers:
        res=re.sub(' +', ' ', lines[index]).strip().split(":")
        #jsdict[name+"_"+res[0]]=  res[1].replace(" ", "")
        jsdict[name+"_"+res[0]]=  re.sub('^ ', ' ', res[1]).strip()
    #print(jsdict)
    return jsdict

def CaseSysbenchFileioResult(context):
    resdict={}
    valdict=CaseSysbenchBaseResult(context,[23,24,25], "fileio")
    for key in valdict:
        resdict[key]= valdict[key].split(" ")[0].split("=")[1]
    print(resdict)
    return resdict

def CaseSysbenchThreadsResult(context):
    return CaseSysbenchBaseResult(context,[13], "threads")

def CaseSysbenchMemoryResult(context):
    return CaseSysbenchBaseResult(context,[23], "memory")

def CaseSysbenchMutexResult(context):
    return CaseSysbenchBaseResult(context,[13,19], "mutex")

def CaseSysbenchCpuResult(context):
    return CaseSysbenchBaseResult(context,[14,26], "cpu")

def CaseSysbenchMysqlResult(context):
    resdict={}
    #valdict=CaseSysbenchBaseResult(context,[23,24,25], "fileio")
    valdict=CaseSysbenchBaseResult(context,[18], "mysql")
    for key in valdict:
        resdict[key]= valdict[key].split(" ")[0]
    print(resdict)
    return resdict

sysbenchresult={
"cpu": CaseSysbenchCpuResult,
"fileio": CaseSysbenchFileioResult,
"mutex": CaseSysbenchMutexResult,
"threads": CaseSysbenchThreadsResult,
"memory": CaseSysbenchMemoryResult,
"mysql": CaseSysbenchMysqlResult,
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
        return sysbenchresult[name](res)
    return ""

def CaseUnixbenchBaseResult(context, numbers, name):
    jsdict={}
    lines=context.split("\n")
    for index in numbers:
        res=re.sub(' +', ' ', lines[index]).strip().split(":")
        #jsdict[name+"_"+res[0]]=  res[1].replace(" ", "")
        jsdict[name+"_"+res[0]]=  re.sub('^ ', ' ', res[1]).strip()
    #print(jsdict)
    return jsdict

def CaseUnixbenchLogfileResult(context):
    sigcpudict={}
    multcpudict={}
    #api.dumpline(context)
    lines=context.split("\n")
    res=lines[-15:-1]
    for line in res:
       line= re.sub('  +', '  ', line).strip()
       linearr=line.split("  ")
       if len(linearr) > 2:
           print(linearr[0], linearr[1].split(" ")[0], linearr[2])
           sigcpudict["sig "+linearr[0]]=linearr[1].split(" ")[0]
           sigcpudict["mult "+linearr[0]]=linearr[2]

    RunSaveBenchJson("unixbench-sig", sigcpudict)
    RunSaveBenchJson("unixbench-mult", sigcpudict)
    #return CaseSysbenchBaseResult(context,[14,26], "cpu")

unixbenchpre={
"shell1":"export PROGDIR=./pgms",
"shell8":"export PROGDIR=./pgms"
}
unixbenchrun={
"dhry2reg":"./pgms/dhry2reg 10",
"whetstone-double":"./pgms/whetstone-double",
"execl":"./pgms/execl 30",
"fstime":"./pgms/fstime -c -t 30 -d ./tmp  -b 1024 -m 2000",
"fsbuffer":"./pgms/fstime -c -t 30 -d ./tmp  -b 256 -m 500",
"fsdisk":"./pgms/fstime -c -t 30 -d ./tmp  -b 4096 -m 8000",
"pipe":"./pgms/pipe 10",
"context1":"./pgms/context1 10",
"spawn":"./pgms/spawn 30",
"syscall":"./pgms/syscall 10",
"shell1":"export UB_BINDIR=./pgms;./pgms/looper 60 pgms/multi.sh 1",
"shell8":"export UB_BINDIR=./pgms;./pgms/looper 60 pgms/multi.sh 8",
"all":"./Run -i 1"
}


unixbenchresult={
"logfile": CaseUnixbenchLogfileResult,
}


def RunUnixbench(name, workdir):
    if unixbenchpre.get(name):
        api.excuteCommand("cd "+workdir+";"+unixbenchpre[name], 1, 1)
    if unixbenchrun.get(name):
        res=api.excuteCommand("cd "+workdir+";"+unixbenchrun[name], 1, 1)
        #print(res)
        api.dumpline(res)

    if unixbenchresult.get(name):
        return unixbenchresult[name](res)

def CaseRedisbenchLogfileResult(context):
    redisdict={}
    #api.dumpline(context)
    lines=context.split("\n")
    for line in lines:
       linearr=line.split(":")
       if len(linearr) > 1:
           print(linearr[0], linearr[1].split(" ")[1])
           redisdict[linearr[0]] = linearr[1].split(" ")[1]

    RunSaveBenchJson("redisbench", redisdict)
    #RunSaveBenchJson("unixbench-mult", sigcpudict)

redisbenchrun={
"base": "redis-benchmark 127.0.0.1 -p 6379 -c 50 -n 10000 -q",
}
redisbenchresult={
"logfile": CaseRedisbenchLogfileResult,
}

wrkbenchrun={
"get": "-t10 -c30 -d 20s -T5s --latency http://{IP}"
}

def RunSaveBenchJson(name, resdict):
    timestr=time.strftime("%Y%m%d%H%M%S", time.localtime())
    benchmarkdict = {"type": "", "name": "", "data": ""}
    benchmarkdict['type']=name
    benchmarkdict['name']=timestr+"_"+name

    benchmarkdict["data"]=resdict
    benchmarkjson=json.dumps(benchmarkdict, ensure_ascii=False,indent=2)
    filename="/tmp/"+benchmarkdict["name"]
    fd=open(filename, "w")
    json.dump(benchmarkdict, fd)
    fd.close()
    print("write ",filename)


def RunSimpleLogfileBench(name, filename):
    print(name)
    lines=open(filename, "r").readlines()
    context="".join(lines)
    if name == "sysbench":
        pass
    elif name == "unixbench":
        unixbenchresult["logfile"](context)
    elif name == "redis":
        redisbenchresult["logfile"](context)

def RunSimpleBench(name, subname):
    resdict={}
    if name == "sysbench":
        if subname == "all":
            for key in sysbenchrun:
                res=RunSysbench(key, "work/sysbench-master/")
                for key in res:
                    resdict[key]=res[key]
            RunSaveBenchJson(name, resdict)
        else:
            RunSysbench(subname, "work/sysbench-master/")
    elif name == "unixbench":
        if subname == "all":
            RunUnixbench(subname, "work/byte-unixbench-master/UnixBench/")
            #RunSaveBenchJson(name, resdict)
        else:
            RunUnixbench(subname, "work/byte-unixbench-master/UnixBench/")


def BuildSimpleBench(name):
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
parser.add_option("-f", "--logfile", type="string", dest="logfile",
                  help="--logfile  logfile") 
parser.add_option("-t", "--type", type="string", dest="type",
                  help="--type log ")
parser.add_option("-c", "--case", type="string", dest="case",
                  help="--case all/sysbench/unixbench/hackbench/wrk/niginx/radis/cpuspec")

(options, args) = parser.parse_args()


if options.install:
    BenchmarkInstall(options.install)
if options.run:
    if options.logfile:
        RunSimpleLogfileBench(options.run, options.logfile)
    elif options.case:
        RunSimpleBench(options.run, options.case)

if options.list:
    for key in benchmark:
        print(key, benchmark[key])
