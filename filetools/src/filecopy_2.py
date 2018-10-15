from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import Manager
import hashlib, os
 
 
class fileCopy:
    def __init__(self, source, target):
        self.source = source
        self.target = target
 
    def __enter__(self):
        self.sf = open(self.source, 'r+b')
        self.tf = open(self.target, 'w+b')
        return self
 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sf.close()
        self.tf.close()
 
    def startCopy(self):
        while True:
            b = self.sf.read(2048)
            if not b:
                break
            self.tf.write(b)
        self.tf.flush()
 
 
def compute_digest(filename):
    BUFSIZE = 2048
    try:
        f = open(filename, 'r+b')
    except IOError:
        return None
    # 确定算法类型
    digest = hashlib.sha512()
    while True:
        chunk = f.read(BUFSIZE)
        if not chunk:
            break
        digest.update(chunk)
    f.close()
    return digest.hexdigest()
 
 
def copyFinish(*args):
    global sourDic, targDic
    source_map = compute_digest(sourDic + args[0][0])
    target_map = compute_digest(targDic + args[0][0])
    if source_map != target_map:
        print("拷贝失败：", args[0][0])
    else:
        args[0][1].put(args[0][0])
 
 
def fileTarget(*args):
    global sourDic, targDic
    with fileCopy(sourDic + args[0], targDic + args[0]) as f:
        f.startCopy()
    return (args[0], args[1])
 
 
def main():
    dic = os.listdir(sourDic)
    dicL = [x for x in dic if not os.path.isdir(sourDic + x)]
    if len(dicL) > 0:
        print("拷贝中. . .")
        q = Manager().Queue()
        p = Pool()
        for fileName in dicL:
            p.apply_async(fileTarget, (fileName, q), callback=copyFinish)
 
        p.close()
        # p.join()
 
        allCount = len(dicL)
        count = 0
        while True:
            item = q.get()
            if item:
                count += 1
                length = str(round((count / allCount)*100, 1)) + "%"
                print("\r拷贝文件: %d, 拷贝进度: %s" % (count, length), end='')
                if count == allCount:
                    print()
                    break
        print("文件拷贝完成: ")
    else:
        print("文件夹为空")
 
 
sourDic = "./files/"
targDic = "./cp_process/"
if __name__ == '__main__':
    main()
