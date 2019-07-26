#!/usr/bin/python
# coding:utf-8
import threading,time,pandas as pd
from FSMonitor import fileModifiedTime,getModifiedInterval
from keras.models import Sequential
from keras import callbacks
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from Queue import Queue
from numpy import concatenate,vstack
from math import sqrt
from sklearn.metrics import mean_squared_error
from util import *


class optModelTread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(optModelTread, self).__init__(*args, **kwargs)

    def run(self):
        while True:
            global model
            model=getModel()
            time.sleep(OPT_MODEL_INTERVAL)


# 将序列转换为监督学习问题
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    # put it all togethe
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg

def getModel():
    train_X=None

    '''
    fileModifiedTime={}
    fileModifiedTime['1']=Queue(11)
    fileModifiedTime['1'].put(10)
    fileModifiedTime['1'].put(20)
    fileModifiedTime['1'].put(30)
    fileModifiedTime['1'].put(40)
    fileModifiedTime['1'].put(60)
    fileModifiedTime['1'].put(80)
    fileModifiedTime['1'].put(90)
    fileModifiedTime['1'].put(100)
    fileModifiedTime['1'].put(120)
    fileModifiedTime['1'].put(130)
    fileModifiedTime['1'].put(140)
    fileModifiedTime['2'] = Queue(11)
    fileModifiedTime['2'].put(1)
    fileModifiedTime['2'].put(2)
    fileModifiedTime['2'].put(3)
    fileModifiedTime['2'].put(4)
    fileModifiedTime['2'].put(6)
    fileModifiedTime['2'].put(8)
    fileModifiedTime['2'].put(9)
    fileModifiedTime['2'].put(10)
    fileModifiedTime['2'].put(12)
    fileModifiedTime['2'].put(13)
    fileModifiedTime['2'].put(14)
    '''
    #将fileModiedTime中维护的所有文件最近修改时间都作为训练集及测试集
    for mt in fileModifiedTime.values():

        if len(getModifiedInterval(list(mt.queue)))<6:       #数据不够构成训练
            continue
        # 将文件的最近修改时间转化成文件的最近修改时间间隔，构建监督学习问题
        reframed = series_to_supervised(getModifiedInterval(list(mt.queue)),5)
        print reframed
        values = reframed.values
        # 分为训练集和测试集,4/5为训练集,1/5为测试集
        sum=len(values)
        train = values[0:int(sum*0.8)]         #
        test = values[int(sum*0.8):]

        # 分为输入和输出
        if train_X is None:
            train_X, train_y = train[:, 0:5], train[:, 5:]
            test_X, test_y = test[:, 0:5], test[:, 5:]
        else:
            train_X=vstack((train_X,train[:,0:5]))
            train_y=vstack((train_y, train[:,5:]))
            test_X=vstack((test_X, test[:,0:5]))
            test_y=vstack((test_y, test[:,5:]))
        '''
        train_X, train_y += train[:,0:5], train[:,5:]
        test_X, test_y += test[:,0:5], test[:,5:]
        '''
    if train_X is None:
        model=None
        return model
    else:
        print train_X
        print test_X
        # 重塑成3D形状 [样例, 时间步, 特征]
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

        # 设计网络
        model = Sequential()
        model.add(LSTM(50, input_shape=(train_X.shape[1], train_X.shape[2])))
        model.add(Dense(1))
        model.compile(loss='mae', optimizer='adam')
        earlyStopping = callbacks.EarlyStopping(monitor='val_loss', patience=5, verbose=1, mode='auto')
        # 拟合网络模型
        history = model.fit(train_X, train_y, epochs=1000,callbacks=[earlyStopping], batch_size=100, validation_data=(test_X, test_y), verbose=2, shuffle=False)


        # 作出预测
        '''
        test=[20.,10.,10.,20.,10.]
        test=series_to_supervised(test, 4).values
        test=test.reshape((test.shape[0], 1, test.shape[1]))
        '''
        model.predict(test_X)

        return model

def getPredict(data):
    global model
    if model==None:
        return 0
    data=series_to_supervised(data, 4).values
    data=data.reshape((data.shape[0], 1, data.shape[1]))
    #temp=model.predict(data)
    return model.predict(data)[0][0]

model=getModel()