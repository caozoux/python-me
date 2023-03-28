#!/bin/python3

import logging
import pyinotify
import time
import os
import sys
import datetime
import schedule

class ProcessTransientFile(pyinotify.ProcessEvent):
    def __init__(self):
        self.machine_crash=[]

    def cleandata(self):
        self.machine_crash=[]

    def process_IN_CREATE(self,event):
        crash_data=[]
        filename = event.pathname
        crash_data.append(time.time())
        crash_data.append(filename)
        self.machine_crash.append(crash_data)
        print(self.machine_crash)
        size=len(self.machine_crash)
        logger.debug("%s add"%event.pathname)
        if size >= 5:
            start=self.machine_crash[-5]
            end=self.machine_crash[-1]
            diff=float(end[0])-float(start[0])
            print(diff,start)
            if diff > 3000:
                pass

handler=""
logger =""

def day_job(arg1):
    handler.cleandata()

# 创建logger对象
logger = logging.getLogger('test_logger')
# 设置日志等级
logger.setLevel(logging.DEBUG)
# 追加写入文件a ，设置utf-8编码防止中文写入乱码
test_log = logging.FileHandler('/tmp/test.log','a',encoding='utf-8')
# 向文件输出的日志级别
test_log.setLevel(logging.DEBUG)
# 向文件输出的日志信息格式
formatter = logging.Formatter('%(asctime)s - %(filename)s - line:%(lineno)d - %(levelname)s - %(message)s -%(process)s')
test_log.setFormatter(formatter)
# 加载文件到logger对象中
logger.addHandler(test_log)


filename = sys.argv[1]

schedule.every().day.at("23:59").do(day_job)
#wm = pyinotify.WatchManager()
#notifier = pyinotify.Notifier(wm)
#wm.watch_transient_file(filename, pyinotify.IN_CREATE, ProcessTransientFile)
multi_event = pyinotify.IN_CREATE
handler= ProcessTransientFile()
wm = pyinotify.WatchManager()
notifier = pyinotify.Notifier(wm, handler)
wm.add_watch(filename, multi_event)
notifier.loop()

