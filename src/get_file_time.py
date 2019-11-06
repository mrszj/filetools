# -*- coding:utf-8 -*-
'''
Created on 2018年11月01日
@author: songzj
@version: 1.0.0
useage:
    python get_file_time.py 目的文件夹或文件
    e.g.
    python get_file_time.py D:\ssdftp\iis\ftp
        获取D:\ssdftp\iis\ftp目录及子目录下最新的文件，打印该文件名及创建、最后修改时间
'''
import time
import os
import sys

def listdir(path, list_name):  #传入存储的list
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        else:
            list_name.append((file_path,os.path.getctime(file_path)))

def newestfile(target_list):
    newest_file = target_list[0]
    for i in range(len(target_list)):
        if i < (len(target_list)-1) and newest_file[1] < target_list[i+1][1]:
            newest_file = target_list[i+1]
        else:
            continue
    return newest_file

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("参数数量不正确，脚本退出")
        sys.exit(1)
    destdir = sys.argv[1] #目的文件夹或文件夹，必须绝对路径
#     destdir = r'D:\ftp'
    file_list = []
    if os.path.isdir(destdir):
        listdir(destdir, file_list)
        new_file = newestfile(file_list)
        mtime = time.ctime(os.path.getmtime(new_file[0]))
        ctime = time.ctime(os.path.getctime(new_file[0]))
        print("newest file is : %s\nLast modified : %s\ncreated time  : %s" % (new_file[0],mtime,ctime))
    else:
        mtime = time.ctime(os.path.getmtime(destdir))
        ctime = time.ctime(os.path.getctime(destdir))
        print("newest file is : %s\nLast modified  : %s\ncreated time   : %s" % (destdir,mtime,ctime))


