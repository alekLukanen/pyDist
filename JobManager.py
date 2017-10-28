#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 13:12:00 2017

@author: alek
"""

import multiprocessing as mp
import threading
import time
import importlib
from Job import JobRunner
from sys import exit

class JobManager(object):
    
    def __init__(self):
        print ('initiating the class...')
        self.job_q = mp.Queue(0) #new jobs go here
        self.result_q = mp.Queue(0) #finished jobs go here
        self.done_q = mp.Queue(0)
        self.running_job_dictionary = {}
        
        self.never_ending = True
        
        self.job_tick = 0
        
        self.job_q_count = 0
        self.job_q_count_lock = threading.Lock()
        
        self.result_q_count = 0
        self.result_q_count_lock = threading.Lock()
        
        self.result_q_removed_count = 0
        self.result_q_removed_count_lock = threading.Lock()
        
        self.done_q_count = 0
        self.done_q_count_lock = mp.Lock()
        
        self.running_job_dictionary_lock = threading.Lock()
        
        self.all_done = threading.Event()
        self.all_done.clear()
        
        self.job_completed = mp.Event()
        self.job_completed.clear()
        
        self.num_processors = mp.cpu_count()
        
        self.job_runner = threading.Thread(name='job_runner_thread', target=self.job_runner)
        self.job_runner.daemon = True
        self.job_runner.start()
        
        self.job_catcher = threading.Thread(name='job_catcher_thread', target=self.job_catcher)
        self.job_catcher.daemon = True
        self.job_catcher.start()
        
    def set_num_processors(self, n):
        self.num_processors = n   
    
    def wait_for_all_results(self):
        print ('waiting for all of the result to come in')
        self.all_done.wait()
        
    def check_all_done(self):
        return self.all_done.is_set()
    
    def get_result(self):
        if (self.never_ending!=True):
            self.result_q_count_lock.acquire()
            if (self.result_q_count==self.result_q_removed_count and self.all_done.is_set()):
                self.result_q_count_lock.release()
                return None
            self.result_q_count_lock.release()
        result = self.result_q.get()
        self.result_q_removed_count_lock.acquire()
        self.result_q_removed_count+=1
        self.result_q_removed_count_lock.release()
        return result
        
        
    #this method retrieves all results found in the done_q Queue. 
    #This method initializes and stores a reference of that particular 
    #job in the running_job_array. once the job has finished it will 
    #place a return value in the done_q.
    def job_catcher(self):
        while(True):
            job_return = self.done_q.get()
            #print ('---> job_manaer_id', job_return.job_manager_id)
            
            #shutdown the process
            self.running_job_dictionary_lock.acquire()
            try:
                ref_job = self.running_job_dictionary.pop(job_return.job_manager_id)
            except:
                #pass
                print ('lost one: %d' % job_return.job_manager_id)
            self.running_job_dictionary_lock.release()
            #try:
                #ref_job.processor.join()
                #print ('joined')
                #ref_job.processor.terminate()
            #except:
                #pass
                #print ('<---> job not started')
            ref_job.processor = None
            self.job_completed.set()
            
            #add the result to the result_q
            self.result_q.put(job_return)
            
            self.result_q_count_lock.acquire()
            self.result_q_count+=1
            self.result_q_count_lock.release()
            
            self.running_job_dictionary_lock.acquire()
            if (len(self.running_job_dictionary)==0 
                and self.result_q_count==self.job_tick):
                self.all_done.set()
            self.running_job_dictionary_lock.release()
        
    def job_runner(self):
        while(True):
            
            #get the length of the
            self.running_job_dictionary_lock.acquire()
            num_running = len(self.running_job_dictionary)
            self.running_job_dictionary_lock.release()
            
            if (num_running<self.num_processors):
                job = self.job_q.get()
                
                self.job_q_count_lock.acquire()
                self.job_q_count -= 1
                self.job_q_count_lock.release()
                
                self.running_job_dictionary_lock.acquire()
                self.running_job_dictionary[job.job_manager_id] = job
                #self.running_job_dictionary_lock.release()
                
                #start the processor...
                #need to start after adding to dictionary
                p = mp.Process(target=self.importLibrary
                                   , args=(job,))
                job.processor = p
                job.processor.start()
                self.running_job_dictionary_lock.release()
            else:
                self.job_completed.wait()
                self.job_completed.clear()
                
        
    def add_job(self, job):
        
        #add the job to the queue
        self.running_job_dictionary_lock.acquire()
        job.job_manager_id = self.job_tick
        self.job_q.put(job)
        self.running_job_dictionary_lock.release()
        
        #increment the counter
        self.job_q_count_lock.acquire()
        self.job_q_count += 1
        self.job_q_count_lock.release()
        
        #increment the ticker
        self.job_tick+=1
        
    
    def importLibrary(self,job):
        i = importlib.import_module(job.file_name)
        func = getattr(i,job.function_name)
        if (len(job.arguements)==0):
            job.return_value = func()
            job.processor = None
            self.done_q.put(job)
            exit(0)
        else:
            job.return_value = func(*job.arguements)
            job.processor = None
            self.done_q.put(job)
            exit(0)
            
        
if __name__ == '__main__':
    print ('starting the job manager')
    jobM = JobManager()
    jobM.set_num_processors(8)
    
    n = 10000000
    N = 1000
    start_time = time.time()
    for i in range(0,N):
        ex_job = JobRunner()
        ex_job.file_name = "exSheet"
        ex_job.function_name = "call_ep"
        ex_job.arguements = (n,)
        jobM.add_job(ex_job)
        
    num_found = 0
    average = 0.0
    while(True):
        #if (jobM.check_all_done() and jobM.job_tick==jobM.)
        result = jobM.get_result()
        if (result==None):
            break
        else:
            average+=result.return_value
            num_found+=1
            
        if (num_found==N):
            break
            
    print ('num_found: %d' % num_found)
    print ('average value: ', average/N)
    jobM.wait_for_all_results()
    print (jobM.check_all_done())
    print ('the program has finished: ', time.time()-start_time)
    
    
