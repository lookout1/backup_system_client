#!/usr/bin/python
# -*- coding:UTF-8 -*-
import transfer,os,xmlFile,threading,time
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
        t=backupThread(args=(sourceFilePath,filename));
        # 将备份线程加入等待队列
        fstat = getFileAttr(sourceFilePath)
        transfer.waitQueue.put((fstat.st_size, t));  # 备份线程的优先级即为文件大小
        t.start()

#根据一定时间间隔,自动备份已经上传的文件
def autoBackup():
    while True:
        # 获取状态为completed的文件路径(客户端)
        fileList = xmlFile.getClientFileListByAttr('state', 'completed')
        for filePath in fileList:
            backUpFile(filePath)
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

        # 创建线程进行文件备份
        t=backupThread(args=(sourceFilePath,destFilePath));
        # 将备份线程加入等待队列
        fstat = getFileAttr(sourceFilePath)
        transfer.waitQueue.put((fstat.st_size, t));  # 备份线程的优先级即为文件大小
        t.start()


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
    xmlFile.modifyFile(destFilePath)
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