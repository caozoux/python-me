import os
import re
import json
import subprocess
from optparse import OptionParser

def excuteCommand(com):
    ex = subprocess.Popen(com, stdout=subprocess.PIPE, shell=True)
    out, err  = ex.communicate()
    status = ex.wait()
    #print("cmd in:", com)
    #print("cmd out: ", out.decode())
    return out

#                  action="store", type="int", default="1", dest="threadsCount",
parser = OptionParser()
parser.add_option("-c", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")

parser.add_option("-t", "--type", type="string", dest="type",
                  help="--type stat_event ")

(options, args) = parser.parse_args()

perfjson = {"type": "", "name": "", "data": ""}
perfkeymap={}
res=excuteCommand("perf stat -e \"kvm:*\" -a sleep 1s 2>&1")
lines=res.decode()
res=re.sub(' +', ' ', lines).strip()
res=re.sub('\n +', '\n', res).strip()
newlines=res.split("\n")
dist=[]
for line in newlines[2:-2]:
    #print(line)
    item=line.split(" ")
    #print(item)
    perfkeymap[item[1]]=int(item[0])
#aa=' '.join(lines.strip())

#print(perfkeymap)
#perfjs=json.dumps(perfkeymap, ensure_ascii=False,indent=2)
#print(perfjs)
perfjson['type']="perf-kvm"
perfjson['name']="perf-kvm-2012"
#perfjson['data']=perfkeymap
perfjson['data']=[perfkeymap]
#print(perfjson['data'])
#exit(1)
test=json.dumps(perfjson, ensure_ascii=False,indent=2)
print(test)
