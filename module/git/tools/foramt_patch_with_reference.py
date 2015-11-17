#!/usr/bin/env python3.4

import os
import sys,time
import subprocess
from clrpr import clrprt
from git import gitApp

if __name__ == "__main__":
    patchname = sys.argv[1]
    log =  sys.argv[2]

    if (gitApp.format_sdk_patch(patchname, log, 0)):
        exit(1)
    exit(0)

