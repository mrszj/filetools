# -*- coding:utf-8 -*-
'''
Created on 2018年9月4日
@author: songzj
@version: 1.0.0
useage:
python D:\ssdftp\stability\delfile.py D:\ssdftp\iis\ftp1 1024 ".SUTMP:.sutmp:.000001" "d:\ssdftp\stability\dest\logs\task1.log" 1800
每隔1800秒删除D:\ssdftp\iis\ftp1目录下，大小为1024字节，以fgapfile开头的文件，忽略后缀名为.SUTMP.sutmp.000001的文件，记录日志
到d:\ssdftp\stability\dest\logs\task1.log_日期.log
'''
import datetime
import os
import sys
from time import sleep
from test.test_tools.test_unparse import for_else


# 获取目录下满足条件的文件，必须以flag开头，不以ignore_filesuffixs结尾
def get_file_list(destdir, flag, ignore_filesuffixs):
    filelist = []
    filelist_tmp = os.listdir(destdir)
    try:
        for filename in filelist_tmp:
            ignore_tmp = []
            filetmp = os.path.join(destdir, filename)
            if os.path.isfile(filetmp):
                if flag == os.path.splitext(filename)[0][0:len(flag)]:
                    for ignore_filesuffix in ignore_filesuffixs:
                        if ignore_filesuffix != os.path.splitext(filename)[1]:
                            ignore_tmp.append("1")
                        else:
                            ignore_tmp.append("0")
                    s_ignore_tmp = set(ignore_tmp)
                    if len(s_ignore_tmp) == 1:
                        for ignore in s_ignore_tmp:
                            if ignore == "1":
                                filelist.append(filetmp)
    except Exception as e:
        print(e)
    return (filelist)


# 判断指定文件夹包含文件数和文件夹大小是否与预期的文件数、大小相等，不判断指定后缀名的文件
def get_file_size(filename, filesize):
    filesize_tmp = 0
    try:
        filesize_tmp = os.path.getsize(filename)
    except Exception as e:
        print(e)
    if int(filesize) == int(filesize_tmp) :
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
    monpath = sys.argv[1]  #监控目录，一般为目的端ftp目录，例如 D:\ssdftp\iis\ftp1
    filesize = sys.argv[2]   #符合删除条件的文件大小
    ignore_filesuffixs = sys.argv[3]    #忽略的后缀名，多个用:分割，例如 例如 .SUTMP:.000001
    logfile = sys.argv[4]   #日志文件，例如 "d:\ssdftp\stability\dest\logs\task1.log"
    sleeptime = sys.argv[5] #每个循环sleep时间
    ignore_filesuffixs = ignore_filesuffixs.split(':')
    flag = "fgapfile"
#     monpath = r"D:\ftp\ftp1"
#     filesize = 22
#     ignore_filesuffixs = r".SUTMP:.sutmp:.000001"
#     logfile = r"D:\ftp\ftp1\deldirlog.txt"
#     sleeptime = 2
#     ignore_filesuffixs = ignore_filesuffixs.split(':')
    if (len(sys.argv) != 6):
        print("参数数量不正确，脚本退出")
        sys.exit(1)
    while 1 == 1:
        path_files = get_file_list(monpath, flag, ignore_filesuffixs)
        for file in path_files:
            if (get_file_size(file, filesize)):
                try:
                    print("准备删除  " + file)
                    os.remove(file)
                    print("删除完毕  " + file)
                    writeLog(logfile, file)
                    print("写入日志成功")
                except Exception as e:
                    print(e)
        print("SLEEPING %s 秒" % sleeptime)
        sleep(int(sleeptime))
