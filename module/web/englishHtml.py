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
import sys
import MySQLdb
 
TRANS_URL='http://fanyi.baidu.com/v2transapi'
ORIGIN_HOST='fanyi.baidu.com'

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

class englishMange:
    def __inif__(self):
        pass

    def initial(self):
        self.o_enDown = enDown()
        self.o_enDown.initial()
        self.db = MySQLdb.connect("localhost","root","w123456","english" )
        self.cursor = self.db.cursor()

    def insertWordDb(self, word, audio_link, chinese):
        sql='insert into englishWords values(0, "'+word+'","'+audio_link.encode('utf-8')+'","'+chinese.encode('utf-8')+'", "")'
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print "err: insert"
            # Rollback in case there is any error
            self.db.rollback()

    def isHas(self,word):
        sql='select * from englishWords where name ="'+word+'"'
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            if len(results) >= 1:
                return results[0];
        except:
            print "err: sql find"
            # Rollback in case there is any error
            self.db.rollback()

        return ""

    def getEnglishAudioAndCh(self, word):
        o_ret=[]
        res=self.isHas(word)
        if res:
            o_ret.append(res[2])
            o_ret.append(res[3])
            return o_ret
        audio_link=self.o_enDown.getEnglishAudio(word)
        if audio_link:
            o_ret.append(audio_link)
        else:
            return ""

        en_chinese = self.o_enDown.getEnglishChinese(word)
        if en_chinese:
            o_ret.append(en_chinese)
        else:
            return ""

        self.insertWordDb(word,audio_link,en_chinese)
        return o_ret

    def getEnglishAudio(self, word):
        res=self.isHas(word)
        if res:
            return res[2]

        return self.o_enDown.getEnglishAudio(word)

    def getEnglishChinese(self, word):
        res=self.isHas(word)
        if res:
            return res[3]

        return self.o_enDown.getEnglishChinese(word)
