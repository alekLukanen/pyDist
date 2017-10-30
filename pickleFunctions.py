# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 14:30:29 2016

@author: alek
"""

import pickle
from tempfile import TemporaryFile

def pickleObj(fileName,obj):
    with open(fileName,'w') as f:
        pickle.dump(obj,f)
    
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

def createPickle(job):
    return pickle.dumps(job, protocol=0)
    
def unPickle(data):
    return pickle.loads(data)
    

if __name__ == '__main__':
    a = ('class','method','...',(1,2,3))
    fil = pickleObjTemp(a,'data')
    obj = unpickleObjTemp(fil)
    print ('obj: ',obj)
    