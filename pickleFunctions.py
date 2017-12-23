# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 14:30:29 2016

@author: alek
"""

import pickle
import cloudpickle
from tempfile import TemporaryFile

def pickleObj(fileName,obj):
    with open(fileName,'w') as f:
        cloudpickle.dump(obj,f)
    
def unpickleObj(fileName):
    with open(fileName) as f:
        return cloudpickle.load(f)
        
def pickleObjTemp(job,data):
    outfile = TemporaryFile()
    cloudpickle.dump([job,data],outfile)
    outfile.seek(0)
    return outfile

def unpickleObjTemp(outfile):
    return cloudpickle.load(outfile)

#functions used to pickle a user pickle
def createPickle(obj):
    return cloudpickle.dumps(obj)
    
def unPickle(data):
    return cloudpickle.loads(data)
#######################################

#functions used to create a server pickle
def createPickleServer(obj):
    return cloudpickle.dumps(obj).decode('latin1')

def unPickleServer(data):
    return cloudpickle.loads(data.encode('latin1'))

def pickleListServer(data_list):
    new_list = []
    for item in data_list:
        new_list.append(item.pickle())
    return new_list

def unPickleListServer(data_list):
    new_list = []
    for item in data_list:
        new_list.append(unPickleServer(item))
    return new_list

#########################################
    
def abc():
    return 1+2+3+4

if __name__ == '__main__':
    a = ('class','method','...',(1,2,3),abc)
    fil = createPickle(a)
    print ('data(fil): ', fil)
    obj = unPickle(fil)
    print ('obj: ',obj)
    
    fil2 = createPickleServer(a)
    print ('data(fil2) ', fil2)
    obj2 = unPickleServer(fil2)
    print ('obj: ', obj2)
    