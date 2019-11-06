# -*- coding:utf-8 -*-
'''
Created on 2018年10月17日
@author: songzj
@version: 1.0.0
useage:
python D:\ssdftp\stability\deldir_ncftpget.py D:\ssdftp\iis\ftp1 11371 19711138012 ".SUTMP:.sutmp:.000001" "d:\ssdftp\stability\dest\logs\task1.log" 1800 mu_ test test 192.168.2.110 /initrd/data/haoxin/ /
每隔1800秒删除D:\ssdftp\iis\ftp1目录下，大小为19711138012字节，文件数量为11371个,以mu_开头的子文件夹，忽略.SUTMP .sutmp .000001文件(不计文件数量和大小)，记录日志
通过ncftpget，下载文件用户test ，密码test，把192.167.2.110目录下的所有文件夹传输到/initrd/data/haoxin/目录下
到d:\ssdftp\stability\dest\logs\task1.log_日期.log；下载ftp服务地址必须按照ftp://*.*.*.*/path添写
'''
import datetime
import os
import shutil
import sys
from time import sleep
import subprocess


# 获取目录下所有文件夹
def get_dir(path,flag):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        if filename.startswith(flag):
            pathTmp = os.path.join(path, filename)
            if os.path.isdir(pathTmp):
                list2.append(pathTmp)
    return (list2)


# 判断指定文件夹包含文件数和文件夹大小是否与预期的文件数、大小相等，不判断指定后缀名的文件
def getDirNumSize(dirPath, dirfilenum=0, dirsize=0, ignore_filesuffixs=""):
    dirfilenum_tmp = 0
    dirsize_tmp = 0
    try:
        for root, dirs, files in os.walk(dirPath):
            for f in files:
                if ignore_filesuffixs != "":
                    if not f.endswith(tuple(ignore_filesuffixs)):
                        dirsize_tmp += os.path.getsize(os.path.join(root, f))
                        dirfilenum_tmp += 1
                else:
                    dirsize_tmp += os.path.getsize(os.path.join(root, f))
                    dirfilenum_tmp += 1
    except Exception as e:
        print(e)
    print("==================")
    print("文件夹%s\n实际文件数量:%s\n期望文件数量:%s\n实际大小:%s\n期望大小:%s" % (dirPath, dirfilenum_tmp, dirfilenum, dirsize_tmp, dirsize))
    if int(dirfilenum) == int(dirfilenum_tmp) and int(dirsize) == int(dirsize_tmp) :
        return True
    else:
        return False


# 写日志
def writeLog(logfile, content):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d')
    time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(logfile + "_" + time1 + ".log", 'a') as f:
            f.write(str(time2) + " " + str(content) + os.linesep)
    except Exception as e:
        print(e)

                    
if __name__ == '__main__':
    
    if (len(sys.argv) != 13):
        print("参数数量不正确，脚本退出")
        sys.exit(1)
    path = sys.argv[1]  # ftp目录全路径，例如 D:\ssdftp\iis\ftp1
    dirfilenum = sys.argv[2]  # 目录下文件夹包含文件数量
    dirsize = sys.argv[3]  # 目录大小
    ignore_filesuffixs = sys.argv[4]  # 忽略的后缀名，以:分割，例如 .SUTMP:.sutmp:.000001
    logfile = sys.argv[5]  # 日志文件路径，例如 "d:\ssdftp\stability\dest\task1.log"
    sleeptime = sys.argv[6]  # 每个循环sleep时间
    flag = sys.argv[7]      #删除文件时判断前缀
    ftpuser = sys.argv[8]          #FTP用户
    ftppasswd= sys.argv[9]        #FTP密码
    ftpip = sys.argv[10]      #FTP地址
    localpath = sys.argv[11]    #本地目录
    ftpgetpath = sys.argv[12]    #FTP下载目录
    ignore_filesuffixs = ignore_filesuffixs.split(':')
    print("忽略的后缀为: "+ str(ignore_filesuffixs))
	
    subprocess.call('ncftpget -DD -u {0} -p {1} -R {2} {3} {4}'.format(ftpuser,ftppasswd,ftpip,localpath,ftpgetpath), shell=True)
    print('ncftpget -DD -u {0} -p {1} -R {2} {3} {4}'.format(ftpuser,ftppasswd,ftpip,localpath,ftpgetpath))
    print('本轮GET文件成功')

#     path = r"D:\ftp\ftp1"
#     dirfilenum = 4
#     dirsize = 225743
#     ignore_filesuffix = r".SUTMP"
#     logfile = r"D:\ftp\ftp1\deldirlog.txt"
    while 1 == 1:
        path_dirs = get_dir(path,flag)
        for d in path_dirs:
            if (getDirNumSize(d, dirfilenum, dirsize, ignore_filesuffixs)):
                try:
                    while 1 == 1:
                        print("准备删除  " + d)
                        shutil.rmtree(d)
                        if (os.path.isdir(d)):
                            print("删除失败了,再次删除")
                            writeLog(logfile, "删除失败了,再次删除")
                            sleep(1)
                            continue
                        else:   
                            print("删除完毕  " + d)
                            writeLog(logfile, d)
                            print("写入日志成功")
                            break
                except Exception as e:
                    print(e)
                    writeLog(logfile,e)
        print("SLEEPING %s 秒" % sleeptime)
        sleep(int(sleeptime))
