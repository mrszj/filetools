# -*- coding:utf-8 -*-
'''
Created on 2019年3月17日
@author: songzhaojun
@version: 1.0.1
useage:
python D:\ssdftp\stability\copydir_ncftpput.py D:\ssdftp\stability\mu D:\ssdftp\iis\ftp1 D:\ssdftp\stability\logs\task1.log 3000 5 mu_ ".SUTMP:.sutmp:.000001" test test 192.168.2.110 / /initrd/data/haoxin/
每隔3000秒拷贝D:\ssdftp\stability\mu目录5次到D:\ssdftp\iis\ftp1目录下,文件夹命名为mu_1..mu_5,传输完成后，ftp1目录下文件数量为空时(忽略以.SUTMP、.sutmp、.000001结尾的文件),删除空目录继续下轮拷贝，记录日志
通过ncftpput，上传文件用户test ，密码test，地址192.168.2.110，把/initrd/data/haoxin/目录下的文件夹传输到根目录下
到d:\ssdftp\stability\task1.log_当前日期.log
'''
import os
import shutil
import sys
from time import sleep
#from builtins import str
import datetime
import subprocess

#获取目录下所有文件夹
def get_dir(path,flag):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        if filename.startswith(flag):
            pathTmp = os.path.join(path, filename)
            if os.path.isdir(pathTmp):
                list2.append(pathTmp)
    return (list2)


#判断指定文件夹下文件数量是否为0
def getDirNumSize(dirPath,ignore_filesuffixs):
    dirfilenum_tmp = 0
    try:
        for root, dirs, files in os.walk(dirPath):
            for f in files:
                if ignore_filesuffixs != "":
                    if not f.endswith(tuple(ignore_filesuffixs)):
                        dirfilenum_tmp += 1
                else:
                    dirfilenum_tmp += 1
    except Exception as e:
        print(e)
    if 0 == int(dirfilenum_tmp):
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

#写日志
def writeLog(logfile,content):
    time1 = datetime.datetime.now().strftime('%Y-%m-%d')
    time2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(logfile + "_" + time1 + ".log",'a') as f:
            f.write(str(time2) + " " + str(content)+os.linesep)
    except Exception as e:
        print(e)
        
if __name__ == '__main__':

    if (len(sys.argv) < 11):
        print("参数数量不正确，脚本退出")
        sys.exit(1)
        
    srcdir = sys.argv[1] #待拷贝的文件夹，例如 D:\ssdftp\stability\mu
    destdir = sys.argv[2] #目的路径，一般为ftp目录，例如 D:\ssdftp\iis\ftp1
    logfile = sys.argv[3]   #日志文件存放路径及名称，例如 "d:\ssdftp\stability\logs\task1.log"
    sleeptime = sys.argv[4] #每个循环sleep时间（秒），sleep后判断目的路径是否为空，为空删除空文件夹继续下一轮拷贝，不为空sleep 30秒继续判断
    dirnum = sys.argv[5]    #每个循环拷贝文件夹数量
    dirprefix = sys.argv[7]    #生成文件时的文件名前缀
    ftpuser = sys.argv[8]          #FTP用户
    ftppasswd= sys.argv[9]        #FTP密码
    ftpip = sys.argv[10]      #FTP地址
    ftpputpath = sys.argv[11]    #FTP上传目录
    ftplocalpath = sys.argv[12]  #本地上传文件
	
    if (len(sys.argv) == 12):
        ignore_filesuffixs = sys.argv[6]      #删除文件时判断前缀
        ignore_filesuffixs = ignore_filesuffixs.split(':')
    else:
        ignore_filesuffixs = ""
    print("忽略的后缀为: "+ str(ignore_filesuffixs))    
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
        r = copyDir(srcdir,destdir,str(dirprefix)+str(i))
        if r:
            writeLog(logfile, destdir + os.path.sep + str(dirprefix)+str(i))
        else:
            print("拷贝失败")
            sys.exit(1)
        if i % int(dirnum) == 0 :
            print("本轮拷贝完成")
            subprocess.call('ncftpput -DD -u {0} -p {1}  -m -R {2} {3} {4}'.format(ftpuser,ftppasswd,ftpip,ftpputpath,ftplocalpath), shell=True)
            print('ncftpput -DD -u {0} -p {1}  -m -R {2} {3} {4}'.format(ftpuser,ftppasswd,ftpip,ftpputpath,ftplocalpath))
            print("本轮PUT完成")
            writeLog(logfile, "本轮拷贝+PUT完成")
            sleep(int(sleeptime))
            #判断目录是否为空,为空删除空文件夹继续下轮拷贝
            isempty = False
            while not isempty:
                path_dirs = get_dir(destdir,dirprefix)
                for d in path_dirs:
                    if (getDirNumSize(d,ignore_filesuffixs)):
                        try:
                            print("准备删除  " + d)
                            shutil.rmtree(d)
                            print("删除完毕  " + d)
                            writeLog(logfile, d)
                            print("写入日志成功")
                        except Exception as e:
                            print(e)
                    else:
                        isempty = False
                        print("目录没有传输完成,等待20秒")
                        sleep(30)
                        break
                    isempty = True
            writeLog(logfile, "删除空目录完成")
        i += 1