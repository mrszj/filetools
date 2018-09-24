#!/usr/bin/env python
#-*- coding:utf-8 -*-
#指定目录,间隔时间,生成指定数量,大小,文件名,记录日志
import time
import os
import sys
# 命令行参数依次接收 文件路径，时间周期，文件数量，文件大小，文件名称，日志路径，日志名称 7个参数
# 执行方式：python create.py E:\python_workplace\test 1000 10 1 liu E:\python_workplace\log log.txt
path = sys.argv[1]
period = int(sys.argv[2])
fileCount = int(sys.argv[3])
fileSize = int(sys.argv[4])
fileName = sys.argv[5]
logPath = sys.argv[6]
logName = sys.argv[7]

# 生成指定周期，指定数量,指定路径，指定大小的文件
def gen_file(period,fileCount,path,fileSize,fileName,logName,logPath):
    i = 1
    while True:
        init_count = 0
        while init_count < fileCount:
            file = open(path + os.sep + fileName + str(i) + 'txt', "w")
            # 以KB为单位
            file.seek(1024 * fileSize)
            file.write('\x00')
            file.close()
            # 记录日志
            file_log = open(logPath + os.sep + logName, "a+")
            file_log.write("第"+str(i)+"个文件创建成功" + os.linesep)

            init_count += 1
            i += 1
        time.sleep(period)
        file_log.close()

gen_file(period,fileCount,path,fileSize,fileName,logName,logPath)

