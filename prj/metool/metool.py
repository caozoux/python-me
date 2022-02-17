#!/bin/python3
import os
import metools
from optparse import OptionParser

#                  action="store", type="int", default="1", dest="threadsCount",
parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list show all commands info")

parser.add_option("-m", "--more", type="string", dest="more",
                  help="--more kernel/initramfs/busbox")
(options, args) = parser.parse_args()

def command_more_handle():
    pass

def command_kernel_handle():
    pass

def command_initramfs_handle():
    pass

def ListToolItems():
    for files in os.listdir("./metools"):
        print(files)

if options.list:
    print(options.list)
elif options.more:
    command_more_handle(options.more)

metools.kernel.kerneltest(1)
aa=metools.kernel.kernel()

