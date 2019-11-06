# -*- coding:utf-8 -*-
'''
Created on 2018年10月29日
@author: songzj
@version: 1.0.0
useage:
python create_multi_dir.py 目的文件夹  生成文件的大小(KB) 横向文件夹数量  纵向文件夹深度  每个文件夹生成文件数量
e.g.
python create_multi_dir.py D:\ssdftp\iis\ftp1\a 1024 5 10 20
在D:\ssdftp\iis\ftp1\a目录下创建横向5级，纵向10级的多级目录，每个目录下均生成20个1024KB(1M)文件。共计50个文件夹,1000个1M文件
'''
import datetime
import os
import sys

# 生成固定大小的文件,以KB为单位
def gen_file(file_path, file_name, file_size):
    with open(file_path + os.sep + file_name, "w") as f:
        f.write('\x00' * 1024 * file_size)

if __name__ == '__main__':
    
    destdir = sys.argv[1] #目的文件夹，必须绝对路径，会在此文件夹下创建多级目录
    file_size = int(sys.argv[2]) #生成文件的大小，为1KB的倍数，为0不创建文件只创建文件夹，为1则生成1KB文件，为1048576为1GB文件
    span = int(sys.argv[3])   #横向文件夹数量，即destdir下一级文件夹数量
    depth = int(sys.argv[4]) #纵向文件夹深度，例如为3时，会生成destdir/1/2/3目录结构
    file_num = int(sys.argv[5])    #每个文件夹下生成文件数量，此脚本总共会生成 span * depth个文件夹，span * depth * filenum个文件
#     destdir = r"D:\ftp\ftp1\xx"
#     file_size = 10
#     span = 5
#     depth = 5
#     file_num = 5
    fileprefix = "fgapfile"
    dir_prefix = "multistage_"
    if (len(sys.argv) != 6):
        print("参数数量不正确，脚本退出")
        sys.exit(1)

    print("*********************************************************")
    print('%-8s''%-8s''%20s' % (" ", span * depth, "folders will be created"))
    print('%-8s''%-8s''%20s' % (" ", span * depth * file_num, "  files will be created"))
    print("*********************************************************")
    
    tmp_destdir = destdir
    dir_count = 0
    dir_print = span * depth / 10
    file_count = 0
    file_print = span * depth * file_num / 10
    starttime = datetime.datetime.now()

    file_seq = 1
    for s in range(1, span + 1):
        # 生成一级目录及文件
        os.makedirs(destdir + os.sep + dir_prefix + str(s), exist_ok=True)
        dir_count += 1
        if dir_count % dir_print == 0:
            print("    " + str(dir_count) + " folders have been created.")
        tmp_destdir = destdir + os.sep + dir_prefix + str(s)
        for f in range(1, file_num + 1):
            gen_file(tmp_destdir, fileprefix + str(f) + ".txt", file_size)
        file_count = file_count + file_num
        if file_count % file_print == 0:
            print("    " + str(file_count) + " files have been created.")
        # 生成二 级+目录及文件
        for d in range(2, depth + 1):
            os.makedirs(tmp_destdir + os.sep + dir_prefix + str(d), exist_ok=True)
            dir_count += 1
            if dir_count % dir_print == 0:
                print("    " + str(dir_count) + " folders have been created.")
            tmp_destdir = tmp_destdir + os.sep + dir_prefix + str(d)
            for f in range(1, file_num + 1):
                gen_file(tmp_destdir, fileprefix + str(f) + ".txt", file_size)
            file_count = file_count + file_num
            if file_count % file_print == 0:
                print("    " + str(file_count) + " files have been created.") 
    endtime = datetime.datetime.now()
    print("*********************************************************")
    print("    all done")
    print("    used " + str((endtime - starttime).seconds) + " s")
