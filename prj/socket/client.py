#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：client.py

import socket               # 导入 socket 模块

s = socket.socket()         # 创建 socket 对象
#host = socket.gethostname() # 获取本地主机名
host = "localhost"
#host = socket.gethostname() # 获取本地主机名
host = "11.165.67.4" # 获取本地主机名
port = 50001                # 设置端口号

s.connect((host, port))
print s.send("connect test")
s.close()
