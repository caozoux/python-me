#!/bin/python3
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
"netperf": "https://github.com/HewlettPackard/netperf/archive/refs/heads/master.zip",
"fio": "local command"
}

#"rand_read":"fio --filename=/tmp/testdata  --rw=write --bs=4k --size=5G --numjobs=1  --name=test",
#"order_read":"fio --filename=/tmp/testdata  --rw=write --bs=4k --size=5G --numjobs=1  --name=test",
#"order_write":"fio --filename=/tmp/testdata  --rw=write --bs=4k --size=5G --numjobs=1  --name=test",
fiorun={
"write":"fio --filename=/tmp/testdata  --rw=write --bs=4k --size=5G --numjobs=1  --name=test --runtime=10",
"read":"fio --filename=/tmp/testdata  --rw=read --bs=4k --size=5G --numjobs=1  --name=test --runtime=10",
"randwrite":"fio --filename=/tmp/testdata  --rw=randwrite --bs=4k --size=5G --numjobs=1  --name=test --runtime=10",
"randread":"fio --filename=/tmp/testdata  --rw=randread --bs=4k --size=5G --numjobs=1  --name=test --runtime=10",
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

    SaveBenchJson("unixbench-sig", sigcpudict)
    SaveBenchJson("unixbench-mult", sigcpudict)
    #return CaseSysbenchBaseResult(context,[14,26], "cpu")

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

    SaveBenchJson("redisbench", redisdict)
    #RunSaveBenchJson("unixbench-mult", sigcpudict)

redisbenchrun={
"base": "redis-benchmark 127.0.0.1 -p 6379 -c 50 -n 10000 -q",
}
redisbenchresult={
"logfile": CaseRedisbenchLogfileResult,
}

def CaseWrkLogfileResult(context):
    wrkdict={}
    #api.dumpline(context)
    lines=context.split("\n")
    #print(context)
    #Requests/sec:   2204.34
    #Transfer/sec:    421.36MB
    #Latency   191.68ms  108.46ms 999.94ms   84.62%
    #Req/Sec   138.25     50.87     1.05k    82.43%
    reqline=lines[-4]
    reqline=re.sub(' +', '', reqline).split(":")
    tranline=lines[-3]
    tranline=re.sub(' +', '', tranline).split(":")
    latencyline=lines[-9]
    latencyline=re.sub('^ +', '', latencyline)
    latencyline=re.sub(' +', ' ', latencyline)
    latencyline=re.sub('ms', '', latencyline).split(" ")
    threadreqline=lines[-8]
    threadreqline=re.sub('^ +', '', threadreqline)
    threadreqline=re.sub(' +', ' ', threadreqline).split(" ")
    #print(reqline)
    #print(tranline)
    #print(latencyline)
    #print(threadreqline)
    wrkdict[reqline[0]]=reqline[1]
    wrkdict[tranline[0]]=tranline[1]
    wrkdict[latencyline[0]]=latencyline[1]
    wrkdict[threadreqline[0]]=threadreqline[1]
    #print(wrkdict)
    SaveBenchJson("wrk", wrkdict)


wrkresult={
"connect": CaseRedisbenchLogfileResult,
"logfile": CaseWrkLogfileResult,
}

wrkrun={
"connect":"./wrk -t 16 -c 1024  -H \"Connection: close\" -d 30 --timeout 1 -d 30 --timeout 1 http://{host}/"
}


#==============================================
#fio performance
#==============================================
def CaseFioNormalfileResult(context, numbers, name):
    jsdict={}
    lines=context.split("\n")
    res=re.sub(' +', ' ', lines[numbers]).replace(",","").strip()
    jsdict[name]=res
    return jsdict

def CaseFioResult(context, name):
    return CaseFioNormalfileResult(context, 5, name)

fioresult={
"write": CaseFioResult,
"read":  CaseFioResult,
"randwrite": CaseFioResult,
"randread":  CaseFioResult,
}

def RunFio(name, workdir):
    if fiorun.get(name):
        res=api.excuteCommand(fiorun[name], 1, 1)

    if fioresult.get(name):
        return fioresult[name](res, name)

#==============================================
#fio performance end
#==============================================


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
parser.add_option("-s", "--description", type="string", dest="description",
                  help="--description case description") 
parser.add_option("-d", "--directory", type="string", dest="directory",
                  help="--directroy work directroy") 
parser.add_option("-c", "--case", type="string", dest="case",
                  help="--case all/sysbench/unixbench/hackbench/wrk/niginx/radis/cpuspec")

(options, args) = parser.parse_args()

"save jion result of benchmark"
def SaveBenchJson(name, resdict):
    timestr=time.strftime("%Y%m%d%H%M%S", time.localtime())
    benchmarkdict = {"type": "", "name": "", "data": ""}
    benchmarkdict['type']=name
    if options.description:
        benchmarkdict['name']=name+"_" + options.description + "_" + timestr;
    else:
        benchmarkdict['name']=name+"_" + timestr;

    print(resdict)
    benchmarkdict["data"]=resdict
    benchmarkjson=json.dumps(benchmarkdict, ensure_ascii=False,indent=2)

    if options.directory:
        filename=os.path.join(options.directory,benchmarkdict["name"])
    else:
        filename=os.path.join("/tmp",benchmarkdict["name"])

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
    elif name == "wrk":
        wrkresult["logfile"](context)

"Run benchmark case as interface entry"
def RunSimpleBench(name, subname):
    resdict={}
    if name == "sysbench":
        if subname == "all":
            for key in sysbenchrun:
                res=RunSysbench(key, "work/sysbench-master/")
                for key in res:
                    resdict[key]=res[key]
        else:
            resdict=RunSysbench(subname, "work/sysbench-master/")
    elif name == "unixbench":
        if subname == "all":
            resdict=RunUnixbench(subname, "work/byte-unixbench-master/UnixBench/")
            #RunSaveBenchJson(name, resdict)
        else:
            resdict=RunUnixbench(subname, "work/byte-unixbench-master/UnixBench/")
    elif name == "fio":
        if subname == "all":
            for key in fiorun:
                res=RunFio(key, "")
                for key in res:
                    resdict[key]=res[key]
        else:
            resdict=RunFio(subname, "")

    SaveBenchJson(name, resdict)

def BuildSimpleBench(name):
    return api.excuteCommand(". ./script/build/"+name+"__build.sh ", 0, 1)

def InstallSimpleBench(name):
    if not os.path.exists("work"):
        os.mkdir("work")
    if benchmark[name]:
        res=api.excuteCommand("wget "+benchmark[name]+ " -O work/"+name+".zip", 0, 1)
        if res:
            printf("wget ",name, "download error")
        res=api.excuteCommand("unzip -o -xd ./work ./work/"+name+".zip", 0, 1)
        #res=api.excuteCommand("./script/build/"+name+"__build.sh", 0, 1)
        BuildSimpleBench(name)

def BenchmarkInstall(name):
    if name == "all":
        pass
    else:
        InstallSimpleBench(name)

if options.install:
    BenchmarkInstall(options.install)

if options.run:
    if options.logfile:
        RunSimpleLogfileBench(options.run, options.logfile)
    elif options.case:
        RunSimpleBench(options.run, options.case)

if options.list:
    for key in benchmark:
        print("%-15s %-30s"%(key, benchmark[key]))
