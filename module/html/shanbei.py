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



def baidu_translate():
    words_name = sys.argv[1]
    quoteStr = urllib.quote(words_name)
    url = 'http://openapi.baidu.com/public/2.0/bmt/translate?client_id=WtzfFYTtXyTocv7wjUrfGR9W&q=' + quoteStr + '&from=auto&to=zh'
    try:
        resultPage = urlopen(url)                               #调用百度翻译API进行批量翻译
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    except Exception, e:
        print 'translate error.'
        print e

    resultJason = resultPage.read().decode('utf-8')                #取得翻译的结果，翻译的结果是json格式
    js = None
    try:
        js = json.loads(resultJason)                           #将json格式的结果转换成Python的字典结构
    except Exception, e:
        print 'loads Json error.'
        print e

    key = u"trans_result"
    if key in js:
        dst = js["trans_result"][0]["dst"]                     #取得翻译后的文本结果
        outStr = dst
    else:
        outStr = words_name                                          #如果翻译出错，则输出原来的文本

def sanbei_translate(words):
    shanlink="https://api.shanbay.com/bdc/search/?word=" + words
    try:
        resultPage = urlopen(shanlink)
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    except Exception, e:
        print 'translate error.'
        print e

    resultJason = resultPage.read().decode('utf-8')                #取得翻译的结果，翻译的结果是json格式
    print resultJason
    js = None
    try:
        js = json.loads(resultJason)                           #将json格式的结果转换成Python的字典结构
    except Exception, e:
        print 'loads Json error.'
        print e

    os.system("rm -f html.log")
    filename = "html.log"
    t = open(filename, "wb")
    t.write(resultJason)
    t.close();

    link = os.popen("cat html.log | cut -d 3 -f 3").read()
    print link
    mp3_link = link[4:-1] +"3"
    print mp3_link
    
    #ret = requests.get("http://words-audio.cdn.shanbay.com/uk/h/he/hello.mp3")
    ret = requests.get(mp3_link)
    if ret.status_code == 200:
        ext = ret.headers["content-type"].split("/")[1]
        filename = words+".%s" % ext
        with open(filename, "wb") as f:
            f.write(ret.content)
        # 不显示mplayer的输出
        log_file = "./mplayer.log"
        with open(log_file, "w") as f:
            subprocess.call(["mplayer", filename], stdout=f, stderr=f)
    else:
        raise Exception("shanbei 服务状态码异常。")


sanbei_translate(sys.argv[1])
