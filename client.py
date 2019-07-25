#!/usr/bin/python
# -*- coding:UTF-8 -*-

import file,os,transfer,LSTM,FSMonitor
from util import *


def main():
    init()
    while True:
        input=raw_input("what do you want to do: ").split()
        command = input[0]
        if(len(input)>1):
            sourceFilePath=input[1]
        if(len(input)>2):
            destFilePath=input[2]

        if command == 'backup':
            file.backUpFile(sourceFilePath)

        elif command == 'restore':
            file.restoreFile(sourceFilePath,destFilePath)

        elif command == 'list':
            # 获取状态为completed的文件并列出
            file.listFile('state', 'completed')
        else :
            os._exit(0)


def init():
    # 与服务器同步user.xml
    file.syncXmlToServer()

    #获取状态为transfering的文件并删除
    file.deleteFile('state','transfering')

    #获取状态为completed的文件并列出
    file.listFile('state', 'completed')

    #启动备份调度线程
    fst = file.schedTread()
    fst.start()

    #启动优化模型线程
    lstmt = LSTM.optModelTread()
    lstmt.start()

    #启动自动备份
    t = threading.Thread(target=file.autoBackup)
    t.start()

main()
