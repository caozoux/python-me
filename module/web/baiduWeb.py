# -*- coding: UTF-8 -*-
import sys
import json
import webBase 
import random
import hashlib
import urllib2                                                                   #导入urllib模块
from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块
from io import StringIO

#class baiduWebInterface
#FUNCTION:
#func getEnglishAudioLink: get the english word audio link

class baiduWebInterface(webBase.enBaseDown):
    def __init__(self):
        self._supportAudio=0
        self._supportChinese=1
        self._q = ''
        self._from = ''
        self._to = ''
        self._appid = -1
        self._key = ''
        self._salt = -1
        self._sign = ''
        self._dst = ''
        self._enable = True

    def getResult(self):
        self._q.encode('utf7')
        #m = str(Trans._appid)+Trans._q+str(Trans._salt)+Trans._key
        m = str(self._appid)+self._q+str(self._salt)+self._key
        m_MD4 = hashlib.md5(m)
        self._sign = m_MD4.hexdigest()
        Url_0 = 'http://api.fanyi.baidu.com/api/trans/vip/translate?'
        Url_1 = 'q='+self._q+'&from='+self._from+'&to='+self._to+'&appid='+str(self._appid)+'&salt='+str(self._salt)+'&sign='+self._sign
        Url = Url_0+Url_1
        PostUrl = Url.decode()
        TransRequest = urllib2.Request(PostUrl)
        TransResponse = urllib2.urlopen(TransRequest)
        TransResult = TransResponse.read()
        data = json.loads(TransResult)
        if 'error_code' in data:
            print 'Crash'
            print 'error:',data['error_code']
            return data['error_msg']
        else:
            self._dst = data['trans_result'][-1]['dst']
            return self._dst

    def initial(self):
        self._q = 'Welcome to use icedaisy online translation tool'
        self._from = 'auto'
        self._to = 'zh'
        self._appid = '20170206000038613'
        self._key = 'q70xa0zuYD91SIXouDn9'
        self._salt = random.randint(10000,99999)

    def getEnglishAudioLink(self,word):
        return ""

    def getEnglishChinese(self,word):
        #self._q = 'Welcome to use icedaisy online translation tool'
        self._q = word
        self._from = 'auto'
        self._to = 'zh'
        self._appid = '20170206000038614'
        self._key = 'q71xa0zuYD91SIXouDn9'
        self._salt = random.randint(10001,99999)
        welcome = self.getResult()
        return welcome
