# -*- coding:utf-8 -*-
'''
Created on 2018年9月4日
@author: szj
@version: 1.0.0
useage:
python D:\ssdftp\stability\deldir.py D:\ssdftp\iis\ftp1 11371 19711138012 ".SUTMP" "d:\ssdftp\stability" 1800
每隔1800秒删除D:\ssdftp\iis\ftp1目录下，大小为13312284892字节，文件数量为3370个的子文件夹，忽略.SUTMP文件，记录日志
到d:\ssdftp\stability\deldir_日期.log
'''
import datetime
import os
import shutil
import sys
from time import sleep


#获取目录下所有文件夹
def get_dir(path):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        pathTmp = os.path.join(path,filename)
        if os.path.isdir(pathTmp):
            list2.append(pathTmp)
    return (list2)

#判断指定文件夹包含文件数和文件夹大小是否与预期的文件数、大小相等，不判断指定后缀名的文件
def getDirNumSize(dirPath,dirfilenum=0,dirsize=0,suffix=""):
    dirfilenum_tmp = 0
    dirsize_tmp = 0
    try:
        for root, dirs, files in os.walk(dirPath):
            for f in files:
                if suffix =="" or os.path.splitext(f)[-1] != suffix:
                    dirsize_tmp += os.path.getsize(os.path.join(root, f))
                    dirfilenum_tmp += 1
    except Exception as e:
        print(e)
    print("==================")
    print("文件夹%s\n实际文件数量:%s\n期望文件数量:%s\n实际大小:%s\n期望大小:%s" %(dirPath,dirfilenum_tmp,dirfilenum,dirsize_tmp,dirsize))
    if int(dirfilenum) == int(dirfilenum_tmp) and int(dirsize) == int(dirsize_tmp) :
        return True
    else:
        return False

#写日志
def writeLog(logdir,content):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d')
    time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(logdir + os.path.sep + "deldir_" + time1 + ".log",'a') as f:
            f.write(str(time2) + " " + str(content)+"\n")
    except Exception as e:
        print(e)            
if __name__ == '__main__':
    path = sys.argv[1]  #ftp目录全路径，例如 D:\ssdftp\iis\ftp1
    dirfilenum = sys.argv[2]    #目录下文件夹包含文件数量
    dirsize = sys.argv[3]   #目录大小
    filesuffix = sys.argv[4]    #忽略的后缀名，例如 .SUTMP
    logdir = sys.argv[5]   #日志文件路径，例如 "d:\ssdftp\stability"
    sleeptime = sys.argv[6] #每个循环sleep时间
#     path = r"D:\ftp\ftp1"
#     dirfilenum = 4
#     dirsize = 225743
#     filesuffix = r".SUTMP"
#     logfile = r"D:\ftp\ftp1\deldirlog.txt"
    while 1 == 1:
        path_dirs = get_dir(path)
        for d in path_dirs:
            if (getDirNumSize(d,dirfilenum,dirsize,filesuffix)):
                try:
                    print("准备删除 "+d)
                    shutil.rmtree(d)
                    print("删除完毕 "+d)
                    writeLog(logdir, d)
                    print("写入日志成功")
                except Exception as e:
                    print(e)
        print("SLEEPING %s 秒" % sleeptime)
        sleep(int(sleeptime))
