# -*- coding:utf-8 -*-
'''
Created on 2018年9月4日
@author: szj
@version: 1.0.0
useage:
D:\ssdftp\stability>python deldir.py D:\ssdftp\iis\ftp1 3370 13312284892 ".SUTMP
" "d:\ssdftp\stability\deldir.log" 1800
每隔1800秒删除D:\ssdftp\iis\ftp1目录下，大小为13312284892字节，文件数量为3370个的子文件夹，忽略.SUTMP文件，记录日志
到d:\ssdftp\stability\deldir.log
'''
import os
import shutil
import sys
from time import sleep
from builtins import str
import datetime
import string

#获取目录下所有文件夹
def get_dir(path):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        pathTmp = os.path.join(path,filename)
        if os.path.isrcdir(pathTmp):
            list2.append(pathTmp)
    return (list2)

#判断指定文件夹包含文件数和文件夹大小是否与预期的文件数、大小相等，不判断指定后缀名的文件
def getDirNumSize(dirPath,dirfilenum=0,dirsize=0,suffix=""):
    dirfilenum_tmp = 0
    dirsize_tmp = 0
    for root, dirs, files in os.walk(dirPath):
        for f in files:
            if suffix =="" or os.path.splitext(f)[-1] != suffix:
                dirsize_tmp += os.path.getsize(os.path.join(root, f))
                dirfilenum_tmp += 1
    print("==================")
    print("文件夹%s\n实际文件数量:%s\n期望文件数量:%s" %(dirPath,dirfilenum_tmp,dirfilenum))
    if int(dirfilenum) == int(dirfilenum_tmp):
        return True
    else:
        return False
    
def copyDir(srcdir,destdir,newdirname):
    if (not os.path.exists(srcdir)) or (not os.path.exists(destdir)):
        print("目录不存在,脚本退出")
        sys.exit(1)
    try:
        shutil.copytree(srcdir,destdir + os.path.sep + str(newdirname))
    except Exception as ex:
        print("拷贝出错:"+str(ex))
        return False
    print("copy "+ destdir + os.path.sep + str(newdirname) + " 成功 ")
    return True
def delEmpty(destdir):
    list1 = []
    fileList = os.listdir(destdir)
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
    return (True)

if __name__ == '__main__':
#     srcdir = sys.argv[1] #待拷贝的文件夹，例如 D:\ssdftp\stability\mu
#     destdir = sys.argv[2] #目的路径，一般为ftp目录，例如 D:\ssdftp\iis\ftp1
#     logfile = sys.argv[3]   #日志文件路径，例如 "d:\ssdftp\stability\copydir.log"
#     sleeptime = sys.argv[4] #每个循环sleep时间（秒），sleep后判断目的路径是否为空，为空删除空文件夹继续下一轮拷贝，不为空sleep 30秒继续判断
#     dirnum = sys.argv[5]    #每个循环拷贝文件夹数量
    srcdir = r"f:\f\1"
    destdir = r"f:\ff"
    sleeptime = 10
    dirnum = 3
    dirprefix = ""
    logfile = r"f:\copydirlog.txt"
    i = 1
    with open(logfile,'a') as f:
        time1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(str(time1)+"\n")
    while i > 0:
        #拷贝文件
        print(i % dirnum)
        print("开始本轮拷贝") 
        r = copyDir(srcdir,destdir,i)
        if r:
            with open(logfile,'a') as f:
                f.write(str(i)+"\n")
        else:
            print("拷贝失败")
            sys.exit(1)
        if i % dirnum == 0 :
            print("本轮拷贝完成")
            sleep(sleeptime)
            #判断目录是否为空,为空删除空文件夹继续下轮拷贝
            while not delEmpty(destdir):
                print("目录没有传输完成,等待20秒")
                sleep(30)
            with open(logfile,'a') as f:
                time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(str(time1)+"\n")
        i += 1