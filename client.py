#!/usr/bin/python
# -*- coding:UTF-8 -*-

import file,os,transfer,LSTM,FSMonitor,sys
from util import *
from PyQt4 import QtGui,QtCore


def init():
    # 与服务器同步user.xml
    file.syncXmlToServer()

    #获取状态为transfering的文件并删除
    file.deleteFile('state','transfering')

    '''
    #获取状态为completed的文件并列出
    file.listFile('state', 'completed')
    '''

    #启动备份调度线程
    fst = file.schedTread()
    fst.start()

    #启动优化模型线程
    lstmt = LSTM.optModelTread()
    lstmt.start()

    #启动自动备份
    t = threading.Thread(target=file.autoBackup)
    t.start()


class Example(QtGui.QWidget):

    def __init__(self):
        super(Example, self).__init__()

        init()

        self.initUI()


    def initUI(self):
        self.sourceFilePath=QtGui.QLineEdit(self)
        chooseFileButton = QtGui.QPushButton("chooseFile", self)
        chooseDirButton = QtGui.QPushButton("chooseDir", self)
        backupButton = QtGui.QPushButton("backup", self)
        self.filesInServer=QtGui.QListWidget(self)
        restoreButton = QtGui.QPushButton("restore", self)
        refreshButton = QtGui.QPushButton("refresh", self)

        self.connect(chooseFileButton, QtCore.SIGNAL('clicked()'),self.chooseFile)
        self.connect(chooseDirButton, QtCore.SIGNAL('clicked()'), self.chooseDir)
        self.connect(backupButton, QtCore.SIGNAL('clicked()'), self.backupFile)
        self.connect(restoreButton, QtCore.SIGNAL('clicked()'), self.restoreFile)
        self.connect(refreshButton, QtCore.SIGNAL('clicked()'), self.listFile)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.sourceFilePath, 1, 0)
        grid.addWidget(chooseFileButton, 1, 1)
        grid.addWidget(chooseDirButton, 1, 2)
        grid.addWidget(backupButton, 1, 3)
        grid.addWidget(self.filesInServer, 2, 0,5,0)
        grid.addWidget(restoreButton, 6, 2)
        grid.addWidget(refreshButton, 6, 3)

        self.setLayout(grid)

        self.setWindowTitle('grid layout')
        self.resize(350, 300)

        self.listFile()
        '''
        qle = QtGui.QListWidget(self)
        qle.addItem('dd')
        qle.addItem('cc')
        '''

    def chooseFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                    '/home')
        self.sourceFilePath.setText(filename)

    def chooseDir(self):
        filename = QtGui.QFileDialog.getExistingDirectory(self, 'Open file',
                    '/home')
        self.sourceFilePath.setText(filename)

    def backupFile(self):
        filePath=self.sourceFilePath.displayText()
        if filePath=="":
            return
        file.backUpFile(str(filePath))

    def restoreFile(self):
        if self.filesInServer.currentItem()==None:
            return
        saveFilePath = QtGui.QFileDialog.getSaveFileName(self, 'Open file','/home')
        file.restoreFile(str(saveFilePath),str(self.filesInServer.currentItem().text()))

    def listFile(self):
        self.filesInServer.clear()
        fileList=file.getFileList('state', 'completed')
        for filePath in fileList:
            self.filesInServer.addItem(filePath)




if __name__ == '__main__':
    app = QtGui.QApplication([])
    ex = Example()
    ex.show()
    os._exit(app.exec_())

'''   
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
'''