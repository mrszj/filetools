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
    for root, dirs, files in os.walk(dirPath):
        for f in files:
            if suffix =="" or os.path.splitext(f)[-1] != suffix:
                dirsize_tmp += os.path.getsize(os.path.join(root, f))
                dirfilenum_tmp += 1
    print("==================")
    print("文件夹%s\n实际文件数量:%s\n期望文件数量:%s\n实际大小:%s\n期望大小:%s" %(dirPath,dirfilenum_tmp,dirfilenum,dirsize_tmp,dirsize))
    if int(dirfilenum) == int(dirfilenum_tmp) and int(dirsize) == int(dirsize_tmp) :
        return True
    else:
        return False

if __name__ == '__main__':
    spath = sys.argv[1] #待拷贝的文件夹，例如 D:\ssdftp\stability\mu
    dpath = sys.argv[2] #目的路径，一般为ftp目录，例如 D:\ssdftp\iis\ftp1
    logfile = sys.argv[3]   #日志文件路径，例如 "d:\ssdftp\stability\copydir.log"
    sleeptime = sys.argv[4] #每个循环sleep时间（秒），sleep后判断目的路径是否为空，为空删除空文件夹继续下一轮拷贝，不为空sleep 30秒继续判断
    dirnum = sys.argv[5]    #每个循环拷贝文件夹数量
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
                    with open(logfile,'a') as f:
                        f.write(d+"\n")
                    print("写入日志成功")
                except Exception as e:
                    print(e)
        print("SLEEPING %s 秒" % sleeptime)
        sleep(sleeptime)

@echo off
set j=1
::set q=1
::set dirPath=D:\ssdftp\iis\ftp1
setlocal enabledelayedexpansion
:bg
echo "开始成文件"
echo %date%%time% >> D:\ssdftp\stability\c.log
for /L %%i in (1,1,5) do (xcopy D:\ssdftp\stability\mu  D:\ssdftp\iis\ftp1\%j%_%%i /S /E /I /H /Y /Q)
echo "生成完毕"
@ping 127.0.0.1 -n 1200 -w 1000 >nul
:kong
echo "等待传输"
for /f "delims=" %%x in ('dir /ad /w /b "D:\ssdftp\iis\ftp1"') do (
    echo %%x
    for /f "tokens=3 delims= " %%k in ('dir /s /a /-c "D:\ssdftp\iis\ftp1\%%x" ^|findstr 个文件') do (
    set z=%%k)
    echo "fdsafds!z!
    if !z! == 0 (rd /s /q "D:\ssdftp\iis\ftp1\%%x" && echo del "D:\ssdftp\iis\ftp1\%%x" >>D:\ssdftp\stability\c.log  )
)
for /f "tokens=3 delims= " %%y in ('dir /s /a /-c "D:\ssdftp\iis\ftp1" ^|findstr 个文件') do (
    set zz=%%y)
echo "fdsafds!zz!
if !zz! == 0 ( goto con )

goto loop
:con
echo "传输完成"
echo %j% >> D:\ssdftp\stability\c.log
set /a j+=1
goto bg

