'''
Created on 2018年9月4日

@author: szj
'''
import os
import sys
import platform
def get_dir_size(path):
    list1 = []
    fileList = os.listdir(path)  # 获取path目录下所有文件
    for filename in fileList:
        pathTmp = os.path.join(path,filename)  # 获取path与filename组合后的路径
        if os.path.isdir(pathTmp):   # 判断是否为目录
            get_dir_size(pathTmp)        # 是目录就继续递归查找
        elif os.path.isfile(pathTmp):  # 判断是否为文件
            filesize = os.path.getsize(pathTmp)  # 如果是文件，则获取相应文件的大小
            list1.append(filesize)      # 将文件的大小添加到列表
    return (sum(list1))
def get_dir(path):
    list2 = []
    fileList = os.listdir(path)  # 获取path目录下所有文件
    for filename in fileList:
        pathTmp = os.path.join(path,filename)  # 获取path与filename组合后的路径
        if os.path.isdir(pathTmp):   # 判断是否为目录       # 是目录就继续递归查找
            list2.append(pathTmp)      # 将文件的大小添加到列表
    return (list2)
def get_file_size(filename):
    filesize = os.path.getsize(filename)  # 如果是文件，则获取相应文件的大小
    return (filesize)
def printPath(level, path):
    global allFileNum
    allFileNum = 0
    dirList = []
    fileList = []
    files = os.listdir(path)
    dirList.append(str(level))
    for f in files:
            if(f[0] == '.'):
                pass
            else:
                dirList.append(f)
            fileList.append(f)
    i_dl = 0
    for dl in dirList:
        if(i_dl == 0):
            i_dl = i_dl + 1
        else:
            print('-' * (int(dirList[0])), dl)
    for fl in fileList:
        print('-' * (int(dirList[0])), fl)
        allFileNum = allFileNum + 1


if __name__ == '__main__':
    print(os.name)
    print(os.path.sep)
    path = sys.argv[1]
    path_dir = get_dir(path)
    for dira in path_dir:
        print(get_dir_size(dira))
#     printPath(1,'d:\ftp')
#     print('总文件数=',allFileNum)
#list1 = [11,33,55,66]
