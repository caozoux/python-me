import codecs
import csv

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", type="string", dest="file",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()

REPORTDICT= \
{
"Total":0,
"HW":0,
"XDP":0,
"noraml":0
}
REPORTCRASHDICT={}


machinedict={}
if options.file:
    fd = codecs.open(options.file, encoding='utf-8-sig')
    for row in csv.DictReader(fd, skipinitialspace=True):
        if not row["hostname"][:4] == "rack":
            #print(row["hostname"])
            #print(row)
            REPORTDICT["Total"] += 1
            #igrnoe hw xdp
            if row["crash_type"] == "hardware error":
                REPORTDICT["HW"] += 1
                continue
            if row["crash_type"] == "xdp bug":
                REPORTDICT["XDP"] += 1
                continue

            if row["crash_cause"] in REPORTCRASHDICT.keys():
                REPORTCRASHDICT[row["crash_cause"]] += 1
            else:
                REPORTCRASHDICT[row["crash_cause"]] = 1

            machinename=row["hostname"]
            if machinename in machinedict.keys():

                REPORTDICT["noraml"] += 1

                machinedata= machinedict[machinename]
                machinedata["count"] += 1
                crashtypedist = machinedata["crash_type"]
                crashcausedist = machinedata["crash_cause"]

                #stor the crash type
                if not row["crash_type"] in crashtypedist.keys():
                   crashtypedist[row["crash_type"]] = 1;
                else:
                   crashtypedist[row["crash_type"]] += 1;

                #stor the crash casue stack
                if not row["crash_cause"] in crashcausedist.keys():
                   crashcausedist[row["crash_cause"]] = 1;
                else:
                   crashcausedist[row["crash_cause"]] += 1;

            else:


                REPORTDICT["noraml"] += 1
                crashtypedist={}
                crashcausedist={}
                machinedata={}
                machinedata["count"]=1
                machinedata["hostname"]=machinename
                machinedata["biz"]=row["biz"]
                machinedata["kernel"]=row["kernel"]
                machinedata["crash_type"] = crashtypedist
                crashtypedist[row["crash_type"]] = 1;
                machinedata["crash_cause"]=crashcausedist
                crashcausedist[row["crash_cause"]] = 1;
                
                machinedict[machinename]=machinedata

sortlist=[]
for key in machinedict.keys():
    sortlist.append(machinedict[key])

for i in range(len(sortlist)):
    for j in range(0,i):
        if sortlist[i-j]["count"] > sortlist[i-j-1]["count"]:
            old=sortlist[i-j-1]
            sortlist[i-j-1] = sortlist[i-j]
            sortlist[i-j] = old

total=0
for item in sortlist:
    print(item)
    total += item["count"]

#for key in machinedict.keys():
#    print("%-60s : %-10d"%(key, machinedict[key]["count"]))

print(REPORTDICT)
print(total)
crashlist = sorted(REPORTCRASHDICT.items(), key=lambda x: x[1])

for item in crashlist:
    crashtext=item[0]
    print(crashtext, item[1])
    for item in sortlist:
        crashcause=item["crash_cause"]
        if crashtext in crashcause.keys():
            print("    %-60s:%-5d %-10s"%(item["hostname"],item["count"],item["biz"]))


