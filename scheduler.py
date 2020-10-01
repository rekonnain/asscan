#!/usr/bin/env python

from multiprocessing import Process, Queue
from uuid import uuid4
import time, sys
from random import random


class Scheduler:
    def __init__(self, maxsize):
        q_in = Queue()
        work_q = Queue(maxsize = maxsize)
        def worker():
            while True:
                sys.stderr.write(">>> qsize=%d waiting=%d\n"%(work_q.qsize(), q_in.qsize()))
                job = q_in.get()
                if job == False:
                    sys.stderr.write("Terminating\n")
                    return
                sys.stderr.write("Got job %s\n"%job.ident)
                work_q.put(job)
                sys.stderr.write("Executing job %s\n"%job.ident)
                def task():
                    job.scan()
                    if job.posthook:
                        sys.stderr.write('Executing post hook for job %s\n'%job.ident)
                        job.posthook()
                    work_q.get()
                    sys.stderr.write("Done with job %s\n"%job.ident)
                p = Process(target = task)
                p.start()
                sys.stderr.write("<<< qsize=%d waiting=%d\n"%(work_q.qsize(), q_in.qsize()))
        self.q_in = q_in
        self.work_q = work_q
        p = Process(target = worker)
        p.start()

    def qsize(self):
        return self.q_in.qsize() + self.work_q.qsize()

    def status(self):
        return "%d / %d"%(self.work_q.qsize(), self.q_in.qsize())
    
    def add_job(self, job):
        self.q_in.put(job, False)

    def stop(self):
        self.q_in.put(False, False)

class idgen:
    def __init__(self):
        self.i=0

    def getid(self):
        self.i += 1
        return "id-%s"%self.i

i = idgen()
    
class FakeScan:
    def __init__(self):
        self.timeout = 2.0 + 5.0 * random()
        self.ident = i.getid()
        self.posthook = None
        
    def scan(self):
        sys.stdout.write("Scanning... %s\n" % self.ident)
        time.sleep(self.timeout)
        sys.stdout.write("Scanned %s\n" % self.ident)

if __name__=='__main__':
    scans = []
    for x in range(100):
        scans.append(FakeScan())
    s = Scheduler(32)
    for x in scans:
        s.add_job(x)
        sys.stderr.write("Added job %s to scheduler\n"%x.ident)
    sys.stderr.write("Done adding jobs to scheduler\n")
    s.stop()
