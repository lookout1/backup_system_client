#!/usr/bin/python
# -*- coding:UTF-8 -*-

import threading
import time
from Queue import PriorityQueue

'''
class transferMg:
    def __init__(self,name,length):
        self.name=name;
        self.length=length;
        self.piror=length;

pq = PriorityQueue()

temp=transferMg("hj",10);
pq.put((-temp.piror,temp))    #插入元素
temp=transferMg("sd",20);
pq.put((-temp.piror,temp))   #插入元素
temp=transferMg("zx",30);
pq.put((-temp.piror,temp))

print pq.queue

print pq.get()[1].name

print pq.queue 
'''


class Job(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.clear()

    def run(self):
        test();

    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

def test():
    self=threading.currentThread()
    while True:
        self._Job__flag.wait()
        print time.time()
        time.sleep(1)

a = Job()
a.start()
a.resume()
print 'ok'

