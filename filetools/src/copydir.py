# -*- coding:utf-8 -*-
'''
Created on 2018年9月4日
@author: songzj
@version: 1.0.0
useage:
python D:\ssdftp\stability\copydir.py D:\ssdftp\stability\mu D:\ssdftp\iis\ftp1 D:\ssdftp\stability\logs\task1.log 3000 5
每隔3000秒拷贝D:\ssdftp\stability\mu目录5次到D:\ssdftp\iis\ftp1目录下，传输完成后，ftp1目录下文件数量为空时，删除空目录继续下轮拷贝，记录日志
到d:\ssdftp\stability\task1.log_当前日期.log
'''
import os
import shutil
import sys
from time import sleep
from builtins import str
import datetime

#获取目录下所有文件夹
def get_dir(path):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        pathTmp = os.path.join(path,filename)
        if os.path.isdir(pathTmp):
            list2.append(pathTmp)
    return (list2)

#判断指定文件夹下文件数量是否为0
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
    print("文件夹%s\n实际文件数量:%s\n期望文件数量:%s" %(dirPath,dirfilenum_tmp,dirfilenum))
    if int(dirfilenum) == int(dirfilenum_tmp):
        return True
    else:
        return False

#拷贝srcdir目录到destdir，重命名为newdirname
def copyDir(srcdir,destdir,newdirname):
    if (not os.path.exists(srcdir)) or (not os.path.exists(destdir)):
        print("目录不存在,脚本退出")
        sys.exit(1)
    try:
        shutil.copytree(srcdir,destdir + os.path.sep + str(newdirname))
    except Exception as ex:
        print("拷贝出错:"+str(ex))
        return False
    print(destdir + os.path.sep + str(newdirname) + " 成功 ")
    return True

#删除指定文件夹下空文件夹
def delEmpty(destdir):
    list1 = []
    fileList = os.listdir(destdir)
    try:
        for filename in fileList:
            pathTmp = os.path.join(destdir,filename)
            if os.path.isdir(pathTmp):
                list1.append(pathTmp)
        for d in list1:
            if (getDirNumSize(d)):
                print("准备删除 "+d)
                shutil.rmtree(d)
                print("删除完毕 "+d)
            else:
                return (False)
    except Exception as e:
        print(e)
        return (False)
    return (True)

#写日志
def writeLog(logfile,content):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d')
    time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(logfile + "_" + time1 + ".log",'a') as f:
            f.write(str(time2) + " " + str(content)+"\n")
    except Exception as e:
        print(e)
if __name__ == '__main__':
    srcdir = sys.argv[1] #待拷贝的文件夹，例如 D:\ssdftp\stability\mu
    destdir = sys.argv[2] #目的路径，一般为ftp目录，例如 D:\ssdftp\iis\ftp1
    logfile = sys.argv[3]   #日志文件存放路径及名称，例如 "d:\ssdftp\stability\logs\task1.log"
    sleeptime = sys.argv[4] #每个循环sleep时间（秒），sleep后判断目的路径是否为空，为空删除空文件夹继续下一轮拷贝，不为空sleep 30秒继续判断
    dirnum = sys.argv[5]    #每个循环拷贝文件夹数量
#     srcdir = r"d:\ftp\ftp1\Oracle11g"
#     destdir = r"d:\ftp\ftp1\1"
#     sleeptime = 10
#     dirnum = 2
#     dirprefix = ""
#     logdir = r"d:\ftp\ftp1"
    i = 1
    writeLog(logfile, "开始拷贝" + srcdir +"到" + destdir +"目录")
    while i > 0:
        #拷贝文件
        print("开始拷贝") 
        r = copyDir(srcdir,destdir,i)
        if r:
            writeLog(logfile, destdir + os.path.sep + str(i))
        else:
            print("拷贝失败")
            sys.exit(1)
        if i % int(dirnum) == 0 :
            print("本轮拷贝完成")
            writeLog(logfile, "本轮拷贝完成")
            sleep(int(sleeptime))
            #判断目录是否为空,为空删除空文件夹继续下轮拷贝
            while not delEmpty(destdir):
                print("目录没有传输完成,等待20秒")
                sleep(30)
            writeLog(logfile, "删除空目录完成")
        i += 1