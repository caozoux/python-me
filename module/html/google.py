#! /usr/bin/env python
#coding=utf-8
import requests

def translate(words):
    import re
    url = ("http://translate.google.cn/translate_a/t?"
    "client=t&hl=zh-CN&sl=en&tl=zh-CN&ie=UTF-8&oe=UTF-8&oc=1&otf=2&ssel=3&tsel=0&sc=1&q=%s")
    ret = requests.get(url % words)
    if ret.status_code == 200:
        RULE_TRANSLATE = re.compile('''([^\[\]]+?)\]\]''')
        match = RULE_TRANSLATE.search(ret.text)
        t, o, s, _ = match.group(1).split(u",")
        print u"译文:", t[1:-1]
        print u"发音:", s[1:-1]
        print ""
    else:
        raise Exception("Google翻译服务状态码异常。")
 
def tts(words):
    import subprocess
    url = "http://translate.google.cn/translate_tts?ie=UTF-8&q=%s&tl=en&total=1&idx=0&textlen=4&prev=input"
    ret = requests.get(url % words)
    if ret.status_code == 200:
        ext = ret.headers["content-type"].split("/")[1]
        filename = "tts.%s" % ext
        with open(filename, "wb") as f:
            f.write(ret.content)
        # 不显示mplayer的输出
        log_file = "./mplayer.log"
        with open(log_file, "w") as f:
            subprocess.call(["mplayer", filename], stdout=f, stderr=f)
    else:
        raise Exception("Google TTS服务状态码异常。")

def main(use_tts=True):
    while 1:
        #在window下raw_input不能直接提示中文，需要u"中文".encode("gbk")
        #为了与平台无关，这里直接提示"English:"
        words = raw_input("English:")
        if words == "x":
            break
        if use_tts:
            tts(words)
        translate(words)

if __name__ == "__main__":
    main(use_tts=True)
