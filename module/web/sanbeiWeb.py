# -*- coding: UTF-8 -*-
import re
import sys
import json
import webBase 
import random
import hashlib
import urllib2                                                                   #导入urllib模块
from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块
from io import StringIO

class sanbeiWebInterface(webBase.enBaseDown):
    def __init__(self):
        self._supportAudio=1
        self._supportChinese=0

    def getEnglishAudioLink(self,word):
        "word: english chars  \
         return: audio web download link"

        shanlink="https://api.shanbay.com/bdc/search/?word=" + word
        res=webBase.PWebBase.webDown(shanlink)

        if res:
            ret = re.search("audio\":\s\".*?mp3",res)
            if ret:
                ret=re.search("http.*", ret.group(0))
                if ret:
                    return ret.group(0)
                else:
                    return ""
        else:
            return ""

        return res
