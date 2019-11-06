# -*- coding: utf-8 -*-
import sys
import datetime
import os
import shutil
import sys
from random import randint
from time import sleep


# 获取目录下所有文件夹
def get_logs(path, flag):
    list2 = []
    fileList = os.listdir(path)
    for filename in fileList:
        if filename.startswith(flag):
            pathTmp = os.path.join(path, filename)
            if os.path.isfile(pathTmp):
                list2.append(pathTmp)
    return (list2)


def add_list(start_num, end_number):
    s = []
    for i in range(start_num, end_number + 1):
        s.append(str(i))
    return s


if __name__ == '__main__':

    if (len(sys.argv) != 4):
        print("参数数量不正确，脚本退出")
        print("python 日志路径 日志名前缀 校验的文件前缀")
        sys.exit(1)
    logpath = str(sys.argv[1])  # 日志路径，例如 D:\ssdftp\iis\ftp1，当前目录可以填写./
    logfile_prefix = str(sys.argv[2])  # 日志文件名前缀
    file_prefix = str(sys.argv[3])  # 日志内容中记录的传输文件的前缀
    file_suffix = '.txt'  # 日志内容中记录的传输文件的后缀，默认.txt

    if not os.path.exists(logpath):
        print("文件或者路径不存在,脚本退出")
        sys.exit(1)
    #     file_suffix = '.txt' #默认文件后缀名
    # #    file_prefix = 'ftp3_file_50M_'   #校验的文件名前缀 如 ftp1_file_1K_
    #     file_prefix = 'ftp1_file_1K_'
    logs_list = get_logs(logpath, logfile_prefix)
    logs_all = []
    for log in logs_list:
        print(log)
        with open(log) as lines:
            for line in lines:
                try:
                    line = line.strip()
                    if not len(line):
                        continue
                    l = line.strip().split()[-1].split(file_prefix)[1].split(file_suffix)[0]
                    logs_all.append(l)
                except Exception as e:
                    #print(e)
                    continue
    miss = []
    print("------------------------------------------")
    print("Min File Num Is :"+ min(logs_all,key=int))
    print("Max File Num Is :"+ max(logs_all,key=int))
    print("------------------------------------------")
    mylist = add_list(int(min(logs_all,key=int)), int(max(logs_all,key=int)))
    miss = list(set(mylist).difference(logs_all))
    miss.sort(key=int)
    if len(miss):
        try:
            lostfile = 'lost_'+ logfile_prefix + '.txt'    
            fd = open(lostfile, 'w', encoding='utf-8')
            print("Min File Num Is :"+ min(logs_all,key=int),file=fd)
            print("Max File Num Is :"+ max(logs_all,key=int),file=fd)
            print(" Lost File Num Is :")
            for m in miss:
                print(m)
                print(m, file=fd)
            fd.close()
        except Exception as e:
            print(e)
    else:
        print(" No Missing Files")
        print("------------------------------------------")