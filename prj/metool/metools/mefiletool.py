import os
import re
import json
import subprocess
import random
from optparse import OptionParser

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-b", "--bs", type="string", dest="byteunit",
                  help="--size  operation sizek")
parser.add_option("-c", "--count", type="string", dest="count",
                  help="--cout operation couts * bs, default is 1k")
parser.add_option("-o", "--offset", type="string", dest="offset",
                  help="--offset operation size")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all")
parser.add_option("-t", "--type", type="string", dest="type",
                  help="--type read or write")
parser.add_option("-f", "--file", type="string", dest="file",
                  help="--file file name")
(options, args) = parser.parse_args()


num=1
if options.byteunit and options.byteunit == "1M":
    bufdata='a'*(1024*1024)
else:
    bufdata='a'*(4096)

if not os.path.exists(options.file):
    print(options.file, "isn't exist, creat")
    fd=os.open(options.file, os.O_RDWR | os.O_CREAT)
else:
    fd=os.open(options.file, os.O_RDWR)

if options.offset:
    os.lseek(fd, int(options.offset), 0)
if options.count:
    num = int(options.count)
if options.type == "write":
    while num > 0:
        os.write(fd, str.encode(bufdata))
        num = num - 1;
elif options.type == "read":
    if options.byteunit and options.byteunit == "1M":
        size =(1024*1024)
    else:
        size =(4096)
    while num > 0:
        os.read(fd,size)
        num = num - 1;
os.close(fd)

