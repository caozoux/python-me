#!/usr/bin/python
# encoding: utf-8
import MySQLdb
# 打开数据库连接
db = MySQLdb.connect("localhost","root","w123456","english" )
# 使用cursor()方法获取操作游标
cursor = db.cursor()
# 使用execute方法执行SQL语句
sql="insert into englishWords values(0, \"test0\",\"https://aaaa\",\"aa\", \"\")"
try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
except:
    # Rollback in case there is any error
    db.rollback()

#cursor.execute("SELECT VERSION()")
# 使用 fetchone() 方法获取一条数据库。
#data = cursor.fetchone()
#print "Database version : %s " % data
# 关闭数据库连接
db.close()
