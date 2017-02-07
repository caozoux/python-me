#!/usr/bin/python
# -*- coding: UTF-8 -*-
from web import webBase;
from web import englishHtml;
import re
import MySQLdb
from optparse import OptionParser;
import sys
import os
import time


def sqldata_connect():
    "connect english word mysql databases"
    db = MySQLdb.connect("localhost","root","w123456","english" )
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # 使用execute方法执行SQL语句

def sqldata_disconnect():
    "disconnect english word mysql databases"
    db.close()

parser = OptionParser()
parser.add_option("-e", "--englishword", action="store",type="string", default="", dest="enWord",
                  help="english word", metavar="DERECTORY")
parser.add_option("-l", "--wordlist", action="store",type="string", default="", dest="enFileList",
                  help="the file of list of english word", metavar="DERECTORY")
(options, args) = parser.parse_args()

o_en = englishHtml.englishMange()
o_en.initial()
if options.enWord:
    audio_link = o_en.getEnglishAudio(options.enWord)
    en_chinese = o_en.getEnglishChinese(options.enWord)
    print audio_link
    print en_chinese.encode('utf-8')

#curl -o /export/disk1T/save/english/accident.mp3 http://media.shanbay.com/audio/uk/accidental.mp3
if options.enFileList:
    lines = open(options.enFileList).readlines()
    for line in  lines:
        word=line[:-1]
        o_list=o_en.getEnglishAudioAndCh(word)
        if not o_list:
            print "err: exit"
            exit()
        audio_link = o_list[0]
        en_chinese = o_list[1]
        #audio_link = o_en.getEnglishAudio(word)
        #en_chinese = o_en.getEnglishChinese(word)
        res = re.search("\w*.mp3",audio_link)
        if res:
            print res.group(0)
            audio_file="/export/disk1T/save/english/"+res.group(0)
            if os.path.exists(audio_file):
                print "find "+audio_file
            else:
                os.system("curl -o "+audio_file+" "+audio_link)
        print audio_link
        print en_chinese.encode('utf-8')
        os.system("notify-send "+word+" "+en_chinese.encode('utf-8'))
        for i in range(8):
            os.system("play "+audio_file)
            if i/3 == 0:
                os.system("notify-send "+word+" "+en_chinese.encode('utf-8'))
            time.sleep(3)

