#!/usr/bin/python
# -*- coding:UTF-8 -*-
import transfer,os,xmlFile,threading,time,LSTM,FSMonitor
from util import *


#列出文件列表（服务器）
def listFile(attrName,attrVal):
    fileList = xmlFile.getFileListByAttr(attrName,attrVal)
    for path in fileList:
        print path


#删除文件（服务器）
def deleteFile(attrName,attrVal):
    fileList = xmlFile.getFileListByAttr(attrName,attrVal)
    for path in fileList:
        transfer.delete(path)
        xmlFile.deleteFileByAttr('path',path)
    # 与服务器同步user.xml
    syncXmlToServer()


#备份文件
def backUpFile(sourceFilePath):
    #如果是目录
    if os.path.isdir(sourceFilePath):
        # 遍历sourceFilePath下所有文件
        os.path.walk(sourceFilePath, visit,None);
    else :
        (filepath,filename)=os.path.split(sourceFilePath)
        #t=threading.Thread(target=backup,args=(sourceFilePath,filename))
        #将文件放入等待队列
        if waitQueue.count(sourceFilePath)==0:
            waitQueue.append(sourceFilePath)
        '''多线程备份
        t=backupThread(args=(sourceFilePath,filename));
        # 将备份线程加入等待队列
        fstat = getFileAttr(sourceFilePath)
        transfer.waitQueue.put((fstat.st_size, t));  # 备份线程的优先级即为文件大小
        t.start()
        '''


#根据一定时间间隔,自动备份已经上传的文件
def autoBackup():
    while True:
        # 获取状态为completed的文件路径(客户端)
        fileList = xmlFile.getClientFileListByAttr('state', 'completed')
        for filePath in fileList:
            fstat = getFileAttr(filePath)
            lastBackupTime = float(xmlFile.getAttrByFilepath(filePath, "backup_time"))  # 文件上次备份时间
            recent_modify_time = fstat.st_mtime  # 文件最近修改时间
            #如果文件备份之后修改过则进行备份
            if lastBackupTime<recent_modify_time:
                if waitQueue.count(filePath) == 0:
                    waitQueue.append(filePath)
        time.sleep(INTERVAL)

#恢复文件
def restoreFile(sourceFilePath,destFilePath):
    # 恢复文件
    transfer.restore(sourceFilePath, destFilePath)
    # 恢复文件属性
    xmlFile.restoreFileAttrFromXml(sourceFilePath, destFilePath)


#将USERXML同步至服务器
def syncXmlToServer():
    #如果客户端存在USERXML则同步至服务器，否则将服务器的同步至客户端
    if os.path.exists(USERXML):
        transfer.backup(USERXML,USERXML)
    else:
        transfer.restore(USERXML,USERXML)

#获取文件属性
def getFileAttr(filePath):
    return os.stat(filePath)

#遍历目录的回调函数
def visit(arg, dirname, names):
    for name in names:

        sourceFilePath = dirname + '/' + name
        destFilePath = name

        #如果是目录则不处理
        if os.path.isdir(sourceFilePath):
            continue

        #将文件放入等待队列
        if waitQueue.count(sourceFilePath) == 0:
            waitQueue.append(sourceFilePath)
        '''多线程备份
        # 创建线程进行文件备份
        t=backupThread(args=(sourceFilePath,destFilePath));
        # 将备份线程加入等待队列
        fstat = getFileAttr(sourceFilePath)
        transfer.waitQueue.put((fstat.st_size, t));  # 备份线程的优先级即为文件大小
        t.start()
        '''


def backup(sourceFilePath,destFilePath):

    userXmlMutex.acquire()
    # 向user.xml中添加正在传输的文件及文件属性
    xmlFile.addFile(sourceFilePath, destFilePath)
    # 同步user.xml至服务器
    syncXmlToServer()
    userXmlMutex.release()

    #传输文件
    transfer.backup(sourceFilePath,destFilePath)

    userXmlMutex.acquire()
    # 将user.xml中对应文件状态改为已完成
    xmlFile.modifyFile(sourceFilePath,"state","completed")
    # 同步user.xml至服务器
    syncXmlToServer()
    userXmlMutex.release()

class backupThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(backupThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.clear()

    def run(self):
        backup(self._Thread__args[0],self._Thread__args[1])

    def wait(self):
        self.__flag.wait()

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

waitQueue=[] #等待进行备份的文件列表

class schedTread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(schedTread, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            schedule()
            if len(waitQueue)==0:
                time.sleep(10)

def schedule():
    maxPrior=-1         #优先级值大的优先级高
    maxPriorFile=""
    nowTime = time.time()
    #选出优先级最大的文件
    for filePath in waitQueue:
        fstat=getFileAttr(filePath)
        fsize=fstat.st_size #文件大小
        lastBackupTime=xmlFile.getAttrByFilepath(filePath,"backup_time") #文件上次备份时间
        timeSinceLastBackup=nowTime-lastBackupTime            #文件距离上次备份的时间
        fileModifiedTimeList=FSMonitor.getRecentModifiedTime(filePath,6)  #文件最近六次修改时间
        if fileModifiedTimeList==None:
            predicted_next_modification_time=0
        else:
            predicted_next_modification_time =LSTM.getPredict(FSMonitor.getModifiedInterval(fileModifiedTimeList)) #获取预测的修改时间
        print filePath+' predicted_next_modification_time：'+str(predicted_next_modification_time)
        if fsize==0:
            prior=0
        else:
            prior=(timeSinceLastBackup+predicted_next_modification_time+fsize)/fsize  #文件备份的优先级
        if prior>maxPrior:
            maxPrior=prior
            maxPriorFile=filePath

    if maxPriorFile=="":
        return
    else:
        (dir,filename) = os.path.split(maxPriorFile)
        backup(maxPriorFile,filename)
        #备份完成后将文件移出队列并监视文件的修改操作
        waitQueue.remove(maxPriorFile)
        if not maxPriorFile in FSMonitor.fileModifiedTime:
            FSMonitor.fsm.add_watch(maxPriorFile)




