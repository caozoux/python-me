#!/bin/python3

import os
import os
import sys
import re
import json
import subprocess
import random
from API import api
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-e", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
parser.add_option("-l", "--list", action="store_true", dest="list",
                  help="--list list all benchmark test name") 
(options, args) = parser.parse_args()

kdict = {
"alllist":"[centos,anlos,openeuler]"
"centos":
"anlos":
"openeuler":
}

