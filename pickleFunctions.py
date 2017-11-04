# -*- coding: utf-8 -*-
"""
Created on Sun Dec 25 14:30:29 2016

@author: alek
"""

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

def createPickle(job):
    return cloudpickle.dumps(job)
    
def unPickle(data):
    return cloudpickle.loads(data)
    

if __name__ == '__main__':
    a = ('class','method','...',(1,2,3))
    fil = pickleObjTemp(a,'data')
    obj = unpickleObjTemp(fil)
    print ('obj: ',obj)
    