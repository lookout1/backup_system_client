#!/usr/bin/python
# -*- coding:UTF-8 -*-
import os,socket,time,Queue
from util import *


''' 多线程传输调度
class schedTread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(schedTread, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            schedule()
            time.sleep(SCHED_INTERVAL)

waitQueue=Queue.PriorityQueue()
transferQueue=Queue.PriorityQueue(MTSIZE)   #传输队列中优先级为负数


def schedule():
    for i in range(MTSIZE):
        if waitQueue.empty():
            break;
        else :
            if not transferQueue.full():
                temp=waitQueue.get();
                transferQueue.put(-temp[0],temp[1]);      #temp[0]为优先级,temp[1]为线程,传输队列中原本优先级低的先出队列
                temp[1].resume();
            else :
                temp1=waitQueue.get();
                temp2=transferQueue.get();
                if temp1[0]<-temp2[0]:           #等待队列中线程(最高优先级)的优先级高于传输队列中的线程(最低优先级),交换两个线程
                    waitQueue.put(-temp2[0],temp2[1]);
                    transferQueue.put(-temp1[0],temp1[1]);
                    temp2[1].pause();
                    temp1[1].resume();
                else :
                    break;
'''

def backup(sourceFilePath,destFilePath):
    s = socket.socket()
    s.connect((HOST,PORT))

    command='backup'
    #发送命令
    s.sendall(command + '\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    #发送文件
    sendFile(s,sourceFilePath,destFilePath)

    s.close()

def restore(sourceFilePath,destFilePath):
    s = socket.socket()
    s.connect((HOST,PORT))

    command = 'restore'
    # 发送命令
    s.sendall(command + '\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    #接收文件
    recvFile(s,sourceFilePath,destFilePath)

    s.close()

def delete(destFilePath):
    s = socket.socket()
    s.connect((HOST,PORT))

    command = 'delete'
    # 发送命令
    s.sendall(command + '\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    #发送服务器文件路径
    s.sendall(destFilePath+'\0')
    #等待删除文件的确认
    buf = s.recv(BUFFSIZE).strip('\0')

    s.close()

def sendFile(s,sourceFilePath,destFilePath):

    #发送服务器文件路径
    s.sendall(destFilePath+'\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    fstat = os.stat(sourceFilePath)
    #发送文件长度
    s.sendall(str(fstat.st_size) + '\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    fi = open(sourceFilePath, 'rb')
    length = fstat.st_size
    bt = threading.currentThread()  #bt为备份线程
    #读取文件内容并发送
    while (length > 0):
        if hasattr(bt,'wait'):  #如果线程不参与调度，线程中没有wait成员函数
            bt.wait()           #检查线程是否能继续发送
        buf = fi.read(BUFFSIZE)
        s.sendall(buf)
        length -= len(buf)
    fi.close()

    #等待确认
    buf = s.recv(BUFFSIZE).strip('\0')

def recvFile(s,sourceFilePath,destFilePath):
    #发送服务器文件路径
    s.sendall(destFilePath+'\0')
    buf = s.recv(BUFFSIZE).strip('\0')

    #接收文件长度
    length=s.recv(BUFFSIZE).strip('\0')
    s.sendall(ACK)
    length=long(length)

    #接收文件
    fo=open(sourceFilePath,'wb')
    while(length>0):
        buf=s.recv(min(BUFFSIZE,length))
        fo.write(buf)
        length-=len(buf)
    fo.close()

    #发送确认
    s.sendall(ACK)
