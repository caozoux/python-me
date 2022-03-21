import os
import re
import json
import subprocess
import random
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
parser.add_option("-r", "--run", type="string", dest="run",
                  help="--run command")
(options, args) = parser.parse_args()

def ExampleFunc():
    pass

mecommandfuncdict={
"example":ExampleFunc
}

mejsonfile={
"command":mecommandfuncdict,
}

def ListCommand():
    for key in mejsonfile["command"]:
        print(("%s  %--20s%--30s")%("command:", key, mejsonfile["command"][key]))

if options.list:
    ListCommand()

if options.run:
    RunCommand(options.run)

