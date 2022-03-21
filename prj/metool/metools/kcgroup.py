
import os
import re
import json
import subprocess
import random
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--cmd", type="string", dest="cmd",
                  help="--cmd stat_event ")
(options, args) = parser.parse_args()

def Memory(arg1):
    """TODO: Docstring for Memory.

    :arg1: TODO
    :returns: TODO

    """
    pass
memorydict={
"logfile": CaseRedisbenchLogfileResult,
}

cgroupdict={
"memory": memorydict,
}
