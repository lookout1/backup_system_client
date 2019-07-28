#!/usr/bin/python
# coding:utf-8

import os,csv,threading,copy,xmlFile
from pyinotify import WatchManager, Notifier,ProcessEvent,IN_MODIFY
from Queue import Queue
import time

# 文件最近几次的修改时间，由FSMonitor维护
fileModifiedTime = {}

class EventHandler(ProcessEvent):
    #当文件发生修改操作时记录修改时间
    def process_IN_MODIFY(self, event):
        now_time=time.time()
        filePath=os.path.join(event.path, event.name).rstrip('/')
        if fileModifiedTime[filePath].full():
            fileModifiedTime[filePath].get()
            fileModifiedTime[filePath].put(now_time)
        else :
            fileModifiedTime[filePath].put(now_time)
        print  "Modify file: %s " % filePath

#根据文件修改时间列表得到文件修改间隔时间列表
def getModifiedInterval(ModifiedTime):
    mi=[]
    temp=copy.copy(ModifiedTime)
    if not len(temp)==0:
        last=temp[0]
        temp=temp[1:]
    for next in temp:
        mi.append(next - last)
        last=next
    return mi

#返回最近n次修改的修改时间
def getRecentModifiedTime(filePath,n):
    if not fileModifiedTime.has_key(filePath):   #第一次备份
        return None
    if fileModifiedTime[filePath].qsize()<n:
        return None
    else:
        return list(fileModifiedTime[filePath].queue)[-n:]

class FSMonitor:
    def __init__(self):
        self.wm=WatchManager()
        self.notifier = Notifier(self.wm, EventHandler())
        #监视所有已经完成备份的文件的修改操作
        fileList = xmlFile.getClientFileListByAttr('state', 'completed')
        for path in fileList:
            self.add_watch(path)

    def add_watch(self,path):
        mask = IN_MODIFY
        fileModifiedTime[path] = Queue(11);
        self.wm.add_watch(path, mask, auto_add=True, rec=True)

    def run(self):
        print 'now starting monitor'
        while True:
            try:
                self.notifier.process_events()
                if self.notifier.check_events():
                    self.notifier.read_events()
            except KeyboardInterrupt:
                self.notifier.stop()
                break

#文件操作监视器
fsm = FSMonitor()
t = threading.Thread(target=fsm.run)
t.start()

'''
# 文件最近几次的修改时间，由FSMonitor维护
fileModifiedTime = {}
'''

'''
def FSMonitor(path='.'):
    wm = WatchManager()
    mask = IN_MODIFY
    notifier = Notifier(wm, EventHandler())
    wm.add_watch(path, mask, auto_add=True, rec=True)
    print 'now starting monitor %s' % (path)
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break

def csv_write(path,data):
    with open(path,'w') as f:
        writer = csv.writer(f,dialect='excel')
        for row in data:
            writer.writerow(row)
    return True
    
if __name__ == "__main__":

    fileModifiedTime['/var/log/syslog']=Queue(10);
    fsm=FSMonitor()
    t = threading.Thread(target=fsm.run)
    t.start()
    fsm.add_watch('/var/log/syslog')
    
    temp=Queue(10)
    temp.put(10)
    temp.put(20)
    temp.put(30)
    print getModifiedInterval(list(temp.queue))
    print temp.queue
'''