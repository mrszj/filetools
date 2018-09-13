'''
Created on 2018年9月4日

@author: szj
'''
import os
import platform

def printPath(level, path):
    global allFileNum
    dirList = []
    fileList = []
    files = os.listdir(path)
    dirList.append(str(level))
    for f in files:
        if(os.path.isdir(path + '/' + f)):
            if(f[0] == '.'):
                pass
            else:
                dirList.append(f)
        if(os.path.isfile(path + '/' + f)):
            fileList.append(f)
    i_dl = 0
    for dl in dirList:
        if(i_dl == 0):
            i_dl = i_dl + 1
        else:
            print('-' * (int(dirList[0])), dl)
            printPath((int(dirList[0]) + 1), path + '/' + dl)
    for fl in fileList:
        print('-' * (int(dirList[0])), fl)
        allFileNum = allFileNum + 1


if __name__ == '__main__':
    print(os.name)
    print(os.path.sep)
#     printPath(1,'d:\ftp')
#     print('总文件数=',allFileNum)
    
    
