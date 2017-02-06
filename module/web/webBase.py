#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")
import json                                                                     #导入json模块
import urllib                                                                   #导入urllib模块
import requests
import subprocess
import os
from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块

#CLASS enDown:
#FUNCTION:
#function getEnglishAudio:    get the english word audio file web link address
#function getEnglishChinese:  get the chinese of english word

class enBaseDown:
    def __init__(self):
        self._supportAudio=0
        self._supportChinese=0
        self.objList=[]

    def initial(self):
        pass

    def isSupportAudio(self):
        return self._supportAudio

    def isSupportChinese(self):
        return self._supportChinese

    def getEnglishAudioLink(self,word):
        return ""

    def getEnglishChineses(self,word):
        return ""

class PWebBase:
    def __init__(self):
        pass;

    @staticmethod
    def webDown(link):
        try:
            resultPage = urlopen(link)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            return ""
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
            return ""
        except Exception, e:
            print 'translate error.'
            print e
            return ""

        resultJason = resultPage.read().decode('utf-8')                #取得翻译的结果，翻译的结果是json格式
        return resultJason
