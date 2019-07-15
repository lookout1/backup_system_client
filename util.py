#!/usr/bin/python
# -*- coding:UTF-8 -*-
import threading

HOST='127.0.0.1'
PORT=12345
BUFFSIZE=4096
ACK='OK\0'
INTERVAL=300 #自动备份文件的时间间隔
USERXML="user.xml"   #记录服务器上用户已经备份的文件和正在传输的文件
userXmlMutex = threading.Lock() #user.xml文件互斥访问锁
MTSIZE = 3 #最大同时进行备份传输的文件数
SCHED_INTERVAL=10 #传输调度的时间间隔