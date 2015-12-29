#!/usr/bin/python
#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")

import json                                                                     #导入json模块
import urllib                                                                   #导入urllib模块
from urllib2 import Request, urlopen, URLError, HTTPError                       #导入urllib2模块

def translate(inputFile, outputFile):
    fin = open(inputFile, 'r')                                              #以读的方式打开输入文件
    fout = open(outputFile, 'w')                                            #以写的方式代开输出文件

    
    for eachLine in fin:                                                    #按行读入文件
        print eachLine 
        line = eachLine.strip()                                         #去除每行首尾可能的空格等
        quoteStr = urllib.quote(line)                                   #将读入的每行内容转换成特定的格式进行翻译
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
            continue

        resultJason = resultPage.read().decode('utf-8')                #取得翻译的结果，翻译的结果是json格式
        print resultJason
        js = None
        try:
            js = json.loads(resultJason)                           #将json格式的结果转换成Python的字典结构
        except Exception, e:
            print 'loads Json error.'
            print e
            continue
    
        key = u"trans_result" 
        if key in js:
            dst = js["trans_result"][0]["dst"]                     #取得翻译后的文本结果
            outStr = dst
        else:
            outStr = line                                          #如果翻译出错，则输出原来的文本

        fout.write(outStr.strip().encode('utf-8') + '\n')              #将结果输出
        
    fin.close()
    fout.close()

if __name__ == '__main__':
    translate(sys.argv[1], sys.argv[2])                                   #通过获得命令行参数获得输入输出文件名来执行，方便


