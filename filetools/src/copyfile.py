# -*- coding:utf-8 -*-
'''
Created on 2019年2月20日
@author: songzhaojun
@version: 1.0.1
useage:
python D:\ssdftp\stability\copyfile.py D:\ssdftp\stability\source\10g.txt D:\ssdftp\iis\ftp1 d:\ssdftp\stability\source\logs\task1.log 3000 5 fgapfile_
每隔3000秒拷贝D:\ssdftp\stability\source\10g.txt文件5次到D:\ssdftp\iis\ftp1目录下,命名为fgapfile_1.txt...fgapfile_5.txt,记录日志
到d:\ssdftp\stability\source\logs\task1.log_日期.log文件中,等待3000秒继续下轮拷贝.
参数6(文件前缀)为可选项,如不填写默认为“fgapfile_”
'''
import os
import shutil
import sys
from time import sleep
import datetime

#拷贝srcfile目录到destdir，重命名为newdirname
def copy_file(srcfile,destdir,new_filename):
    full_name = destdir + os.path.sep + new_filename
    try:
        shutil.copy(srcfile,full_name)
		#shutil.copy2(srcfile,full_name)
    except Exception as ex:
        print("拷贝出错:"+str(ex))
        return False
#    print(full_name + " 成功 ")
    return True

#删除指定文件夹下空文件夹
def isempty(destdir,fileprefix):
    fileList = os.listdir(destdir)
    try:
        for filename in fileList:
            filetmp = os.path.join(destdir,filename)
            if os.path.isfile(filetmp):
                if fileprefix == os.path.splitext(filename)[0][0:len(fileprefix)]:
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
            f.write(str(time2) + " " + str(content)+ os.linesep)
    except Exception as e:
        print(e)
        
        
if __name__ == '__main__':
    
    if (len(sys.argv) < 6):
        print("参数数量不正确，脚本退出")
        sys.exit(1)    
    srcfile = sys.argv[1] #待拷贝的文件，例如 D:\ssdftp\stability\source\1K.txt
    destdir = sys.argv[2] #目的路径，一般为ftp目录，例如 D:\ssdftp\iis\ftp1
    logfile = sys.argv[3]   #日志文件存放路径，例如 "d:\ssdftp\stability\source\logs\task1.log"
    sleeptime = sys.argv[4] #每个循环sleep时间（秒），sleep后判断目的路径文件数量是否为0，为0继续下一轮拷贝，不为0sleep 1秒继续判断
    filenum = sys.argv[5]    #每个循环拷贝文件数量
    if (len(sys.argv) == 7):
        fileprefix = sys.argv[6]
    else:
        fileprefix = "fgapfile_"    #生成文件时的文件名前缀

#     srcfile = r"E:\测试部\光闸稳定性测试脚本\source\stability\source\50M.txt"
#     destdir = r"D:\ssdftp\iis\ftp1"
#     logfile = r"E:\测试部\光闸稳定性测试脚本\source\stability\source\logs\task1.log"
#     sleeptime = 10
#     filenum = 5

    if (not os.path.isfile(srcfile)) or (not os.path.exists(destdir)):
        print("文件或者路径不存在,脚本退出")
        sys.exit(1)
    writeLog(logfile, "开始拷贝" + srcfile +"到" + destdir +"目录")
    file_seq = 1
    while file_seq > 0:
        #拷贝文件
#        print("开始拷贝")
        new_filename = fileprefix + str(file_seq) + ".txt"
        r = copy_file(srcfile,destdir,new_filename)
        if r:
            writeLog(logfile, destdir + os.path.sep + str(new_filename))
        else:
            print("拷贝失败")
            sys.exit(1)
        if file_seq % int(filenum) == 0 :
            print("本轮拷贝完成")
            writeLog(logfile, "本轮拷贝完成")
            sleep(int(sleeptime))
            
            #判断目录是否为空,为空继续下轮拷贝
            while not isempty(destdir,fileprefix):
                print("目录没有传输完成,等待2秒")
                sleep(5)
            writeLog(logfile, "本轮文件传输完成")
        file_seq += 1
        