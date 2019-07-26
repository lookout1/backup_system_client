#!/usr/bin/python
# -*- coding:UTF-8 -*-
import time,os,xml.etree.ElementTree as ET
from util import *



def addFile(sourceFilePath,destFilePath):
    now_time = time.time()

    #获取文件属性
    fstat = os.stat(sourceFilePath)

    #向user.xml中添加文件和文件属性
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    #查找是否原来已经上传了此文件
    isExistFile=False
    for file in fileList.iter('file'):
        if(file.attrib['path']==destFilePath):
            file.attrib = {"clientPath":sourceFilePath,\
                      "path": destFilePath,\
                      "state": "transfering", \
                      "st_mode": str(fstat.st_mode), \
                      "st_uid": str(fstat.st_uid), \
                      "st_gid": str(fstat.st_gid), \
                      "st_atime": str(fstat.st_atime), \
                      "st_mtime": str(fstat.st_mtime), \
                      "backup_time": str(now_time)
                           }
            isExistFile=True
            break
    #不存在则添加
    if (not isExistFile) :
        newFile = ET.Element("file")
        newFile.attrib = {"clientPath":sourceFilePath,\
                          "path": destFilePath, \
                          "state": "transfering", \
                          "st_mode": str(fstat.st_mode), \
                          "st_uid": str(fstat.st_uid), \
                          "st_gid": str(fstat.st_gid), \
                          "st_atime": str(fstat.st_atime), \
                          "st_mtime": str(fstat.st_mtime), \
                          "backup_time": str(now_time)
                          }
        fileList.append(newFile)
    tree.write(USERXML)

#修改对应文件的文件属性
def modifyFile(sourceFilePath,attrName,attrVal):
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    for file in fileList.iter('file'):
        if(file.attrib['clientPath']==sourceFilePath):
            file.attrib[attrName]=attrVal
            break
    tree.write(USERXML)

#根据xml记录的属性恢复对应文件的属性
def restoreFileAttrFromXml(sourceFilePath,destFilePath):
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    for file in fileList.iter('file'):
        if (file.attrib['path'] == destFilePath):
            file.attrib['state'] = 'completed'
            os.chmod(sourceFilePath,long(file.attrib['st_mode']))
            os.chown(sourceFilePath,long(file.attrib['st_uid']),long(file.attrib['st_gid']))
            os.utime(sourceFilePath, (float(file.attrib['st_atime']), float(file.attrib['st_mtime'])))
            break

#根据属性值获取对应文件列表(服务器上)
def getFileListByAttr(attrName,attrVal):
    fl=[]
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    for file in fileList.iter('file'):
        if (file.attrib[attrName] == attrVal):
         fl.append(file.attrib['path'])
    return fl

#根据属性值获取对应文件列表(客户端)
def getClientFileListByAttr(attrName,attrVal):
    fl=[]
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    for file in fileList.iter('file'):
        if (file.attrib[attrName] == attrVal):
         fl.append(file.attrib['clientPath'])
    return fl

#根据文件路径获取相应属性值
def getAttrByFilepath(filepath,attrName):
    userXmlMutex.acquire()
    tree = ET.parse(USERXML)
    userXmlMutex.release()
    fileList = tree.getroot()
    attrVal = None
    for file in fileList.iter('file'):
        if (file.attrib['clientPath'] == filepath):
            attrVal=file.attrib[attrName]
            break
    if attrVal==None:
        attrVal=0
    return float(attrVal)

#根据属性值删除对应文件(服务器)
def deleteFileByAttr(attrName,attrVal):
    tree = ET.parse(USERXML)
    fileList = tree.getroot()
    for file in fileList.iter('file'):
        if (file.attrib[attrName] == attrVal):
         fileList.remove(file)
    tree.write(USERXML)

