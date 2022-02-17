import os
import re
import json
import subprocess
from optparse import OptionParser
from API import api


parser = OptionParser()
parser.add_option("-c", "--host", type="string", dest="host",
                  help="--host host ip")

parser.add_option("-i", "--interval", type="string", dest="interval",
                  help="--inerval interval time")
parser.add_option("-n", "--number", type="string", dest="number",
                  help="--number ping package counts")

(options, args) = parser.parse_args()

cmd="ping"
if options.host == "":
    print("Err: host ip no specify")
    exit(1)


cmd=cmd+ " "+options.host

if options.interval:
    cmd=cmd+ " -i "+ options.interval

if options.number:
    cmd=cmd+ " -c "+ options.number

jsondata={}
res=api.excuteCommand(cmd, 1)
lines=res.split("\n")[1:-5]
for line in lines:
    item=line.split(" ")
    key=item[4].replace("icmp_seq=", "")
    value=item[6].replace("time=", "")
    jsondata[key]=value

jsonstr=json.dumps(jsondata, ensure_ascii=False,indent=2)
print(jsonstr)

