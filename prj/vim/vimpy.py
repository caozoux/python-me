#!/usr/bin/env python2.7

import os
import sys
import re
from vimscript import vimobjcomplete

if __name__ == "__main__":
    comManger= vimobjcomplete.ObjCompleteManger(sys.argv[1], sys.argv[2])
    comManger.transferToHead()
    comManger.dump()
    #for obj in comManger.headObjList:
    #    print obj.dump()
    #comManger.dump()
