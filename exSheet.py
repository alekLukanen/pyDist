# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 17:48:28 2016

@author: alek
"""

import numpy as np
import time as tm
import pickle
import importlib
from tempfile import TemporaryFile

def printPi():
    print ('-* this is py: ', np.pi)
    tm.sleep(1)
    return np.pi
    
def printArg(arg0,arg1,arg2):
    answer = arg0+arg1+arg2
    print ('- answer: ', answer)
    tm.sleep(arg0)
    return (arg0,arg1,arg2,answer)    
    
def estimatePi(n):
    inside=0
    np.random.seed()
    for i in range(0,n):
        x=np.random.random_sample()
        y=np.random.random_sample()
        if np.sqrt(x*x+y*y)<=1:
            inside += 1
    pi = 4.0 * inside / n
    return pi
    
def pickleObj(fileName,job,data):
    with open(fileName,'w') as f:
        pickle.dump([job,data],f)
    
def unpickleObj(fileName):
    with open(fileName) as f:
        return pickle.load(f)
        
def pickleObjTemp(job,data):
    outfile = TemporaryFile()
    pickle.dump([job,data],outfile)
    outfile.seek(0)
    return outfile

def unpickleObjTemp(outfile):
    return pickle.load(outfile)
        
def call(className,methodName,args):
    print ('___________________')
    i = importlib.import_module('exSheet')
    func = getattr(i,'printArg')
    print ('-* done...')
    try:
        func(*args)
    except Exception as e:
        print ('call[error]: ',e)
    
if __name__ == '__main__':
    #estimatePi()
    a = ((1,2,3),1,np.zeros(5))
    fil = pickleObjTemp(('class','method','...'),'data')
    obj = unpickleObjTemp(fil)
    print ('obj: ',obj)
    '''
    print 'a: ',a
    pickleObj('objs.pickle',('class','method','...'),'data')
    print 'obj0: ', unpickleObj('objs.pickle')
    call('exSheet','printArgs',args=((1,2,3),1,'a'))
    '''
    
    
