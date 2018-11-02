# -*- coding:utf-8 -*-
'''
Created on 2018年10月29日
@author: songzj
@version: 1.0.0
useage:
python create_file.py 目的文件夹前缀  目的文件夹最大编号 文件大小KB 文件数量
e.g.
python create_file.py D:\ssdftp\iis\ftp 5 1024 100
分别在D:\ssdftp\iis\ftp1至D:\ssdftp\iis\ftp5五个目录下，生成100个1024KB(1M)文件。共计500个1M文件
'''
import datetime
import os
import sys

# 生成固定大小的文件,以KB为单位
def gen_file(file_path, file_name, file_size):
    if file_size > 4194304:
        for size in range(1,int(file_size/1048576)+1):
            with open(file_path+os.sep+file_name,"a+") as f:
                f.write('\x00' * 1024 * 1048576)
                f.flush()
    else:
        with open(file_path + os.sep + file_name, "w") as f:
            f.write('\x00' * 1024 * file_size)
            f.flush()

if __name__ == '__main__':
    
    destdir_pre = sys.argv[1] #目的文件夹，必须绝对路径，不带数字编号
    dir_num = int(sys.argv[2])   #目的文件夹数量，取1为 destdir_pre1一个文件夹、5则为destdir_pre1-5五个文件夹
    file_size = int(sys.argv[3]) #生成文件的大小，以KB为单位，为1则生成1KB文件，为1048576为1GB文件
    file_num = int(sys.argv[4])    #每个文件夹下生成文件数量
#     destdir_pre = r"D:\ftp\ftp"
#     dir_num = 5
#     file_size = 1024
#     file_num = 100
    fileprefix = "fgapfile"
    if (len(sys.argv) != 5):
        print("参数数量不正确，脚本退出")
        sys.exit(1)
    file_print = file_num / 10
    starttime = datetime.datetime.now()
    for i in range(1,dir_num+1):
        destdir = destdir_pre+str(i)
        print(destdir)
        for j in range(1,file_num+1):
            gen_file(destdir,fileprefix+str(j)+".txt",file_size)
            if j % file_print == 0:
                print("    " + str(j) + " files have been created.")
    endtime = datetime.datetime.now()
    print("*********************************************************")
    print("    all done")
    print("    used " + str((endtime - starttime).seconds) + " s")
