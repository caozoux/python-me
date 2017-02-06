# -*- coding: UTF-8 -*-
import webBase
import re
import json                                                                     #导入json模块

#! /usr/bin/env python3
#coding=utf-8
import sys
import json
import random
import hashlib
import urllib2                                                                   #导入urllib模块
import baiduWeb
import sanbeiWeb

from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块
from io import StringIO
 
TRANS_URL='http://fanyi.baidu.com/v2transapi'
ORIGIN_HOST='fanyi.baidu.com'
 
class Result:
    def __init__(self, src, dest, meanings=None):
        self.src=src
        self.dest=dest
        self.meanings=meanings

    def parse_from_json(json_data):
        trans_data=json_data['trans_result']['data'][0]
        try:
            dict_data=json_data['dict_result']['simple_means']['symbols'][0]['parts']
            means=list()
            for item in dict_data:
                tmp=item['means']
                if isinstance(tmp[0],dict):
                    for t_item in tmp:
                        means.append(t_item['word_mean'])
                else:
                    means.append(tmp)
        except KeyError:
            means=None
        return Result(trans_data['src'],trans_data['dst'],means)

    def show(self,file=sys.stdout):
        str_template='<<<translate\n%s--->%s\n<<<meaning\n%s'
        print(str_template % (self.src, self.dest, self.meanings))


def handle_result(content):
    json_data=json.loads(content)
    Result.parse_from_json(json_data).show()

def compose_request(word):
    r"""
    compose urllib.request.Request object accordingly

    """
    body=StringIO()
    body.write('from=en&to=zh' if is_eng(word) else 'from=zh&to=en')
    body.write('&')
    body.write(urllib.parse.urlencode({'query': word }, encoding='utf-8'))
    body.write('&transtype=trans&simple_means_flag=3')
    body=body.getvalue()

    headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest'
        }
    return urllib.request.Request(TRANS_URL, body.encode(encoding='utf-8'), headers=headers, origin_req_host=ORIGIN_HOST, method='POST')

def is_eng(word):
    r"""
    determine whether the unicode char is english or not

    >>> is_eng('hello')
    True
 
    >>> is_eng('你好')
    False
 
    >>> is_eng('\'')
    True
 
    >>> is_eng('‘')
    False
 
    """
    for uchar in word:
        if len(uchar.encode('utf-8'))==1:
            continue
        else:
            return False
    return True



class enDown:
    def __init__(self):
        self.objWebInterList=[]
        self.master="sanbei"

    def bindWebInterface(self, webInterface):
        self.objWebInterList.append(webInterface);

    def initial(self):
        o_baiduInterface = baiduWeb.baiduWebInterface();
        o_baiduInterface.initial()
        o_sanbeiInterface = sanbeiWeb.sanbeiWebInterface();
        o_sanbeiInterface.initial()
        self.bindWebInterface(o_baiduInterface)
        self.bindWebInterface(o_sanbeiInterface)

    def getEnglishAudio(self, word):
        "word: english chars  \
         return: audio web download link"

        for obj in self.objWebInterList:
            if obj.isSupportAudio():
                ret=obj.getEnglishAudioLink(word)
                if ret:
                    return ret

        return
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

    def getEnglishChinese(self, word):
        for obj in self.objWebInterList:
            if obj.isSupportChinese:
                ret=obj.getEnglishChinese(word)
                if ret:
                    return ret
