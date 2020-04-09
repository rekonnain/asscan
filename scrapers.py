#!/usr/bin/env python3

from scanners import Job
from multiprocessing import Process, Queue
import os, sys, re, json
from os.path import join
import collections

debug=True
def d(m):
    if debug:
        sys.stderr.write("> %s\n"%m)

# generic scrape job. is able to run a shell script against one target
# at a time, expecting the script to save something as 1.2.3.4.png
# and generates a results json file that can be then read
# and the filename pattern and command line can be overridden
class ScraperJob(Job):
    def __init__(self, processes=4):
        super().__init__()
        self.path = 'results'
        self.scantype = 'scraper'
        # override
        self.commandline = lambda scheme, target, port: target
        self.output_filename_pattern = '([0-9.]+)\.png'
        self.port = '-1'
        self.scheme = ''
    
    def scan(self):
        d("scraper job targets %s"%str(self.targets))
        if len(self.targets) == 0:
            d("scraper job: no targets, not doing shit")
            return
        os.chdir(self.path) # the uuid id of the scan job
        try:
            os.mkdir(self.ident)
        except:
            pass
        os.chdir(self.ident)
        os.mkdir('output') # reasonable, don't change

        # be careful if changing the queue size. Some jobs, such as the rdp screenshot,
        # create actual (offscreen) X11 windows that are then screenshot. Having more
        # than one job in parallel can cause a fuckup.
        targetqueue = Queue(maxsize = 1) 
        processes = []
        def scrapetask(target):
            targetqueue.put(target)
            c=self.commandline(self.scheme, target, self.port)
            d(c)
            os.system(c)
            targetqueue.get()
        for t in self.targets:
            p = Process(target = lambda: scrapetask(t))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        self.postprocess()
        sys.stderr.write("scraper task done\n")

    def postprocess(self):
        results = []
        re_filename = re.compile(self.output_filename_pattern)
        for x in os.listdir('output'):
            m = re_filename.match(x)
            if m and m.groups():
                ip = m.groups()[0]
                results.append({'host': ip, 'scantype': self.scantype,'port': self.port, 'file': join('output',x)})
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': self.scantype,
                 'jobid': self.ident,
                 'target': self.targets }
        if self.port != '-1':
            meta['port'] = self.port
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()

# simple enough job to be handled by the superclass
class RdpScreenshot(ScraperJob):
    def __init__(self, targets, processes=4, domain='', user='', password=''):
        super().__init__(processes)
        self.targets = targets
        d("rdpscreenshot u=%s d=%s p=%s targets %s"%(user,domain,password,str(self.targets)))
        self.scantype='rdpscreenshot'
        # run the rdp-screenshotter script with an offscreen window
        self.commandline = lambda scheme, target, port: "xvfb-run -a ../../RDP-screenshotter.sh %s '%s' '%s' '%s'"%(target, domain, user, password)
        self.output_filename_pattern = '([0-9.]+)\.png'
    
class VncScreenshot(ScraperJob):
    def __init__(self, targets, port='5901', processes=4, password = ''):
        super().__init__(processes)
        self.targets = targets
        self.scantype = 'vncscreenshot'
        self.port = port
        self.commandline = lambda scheme, target, port: "../../scanners/vnc.py %s::%s %s output/%s.png "%(target, port, password, target)
        self.output_filename_pattern = '([0-9.]+)\.png'
        
        
        
class WebScreenshot(ScraperJob):
    def __init__(self, targets, scheme, port, processes=4):
        super().__init__(processes)
        self.targets = targets
        self.port = port
        self.scheme = scheme
        d("webscreenshot targets %s"%str(self.targets))
        self.path = 'results'
        self.scantype='webscreenshot'
        self.targets = targets
        self.commandline = lambda scheme, target, port: "QT_QPA_PLATFORM=offscreen webscreenshot -r phantomjs %s://%s:%s >/dev/null 2>&1"%(scheme,target,port)
        self.output_filename_pattern = '([a-z]+)_([0-9.]+)_([0-9]+).png'

    # overridden here because of the different path and different regex to match results files
    def postprocess(self):
        results = []
        re_filename = re.compile(self.output_filename_pattern)
        for x in os.listdir('screenshots'):
            m = re_filename.match(x)
            if m and m.groups():
                ip = m.groups()[1]
                port = m.groups()[2]
                results.append({'host': ip, 'scantype': 'web-screenshot', 'port': port, 'file': join('screenshots',x)})
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': 'webscreenshot',
                 'jobid': self.ident,
                 'target': self.targets,
                 'port': self.port }
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()

            
class Enum4Linux(ScraperJob):
    def __init__(self, targets, processes=4, domain='', user='', password=''):
        super().__init__(targets)
        self.path = 'results'
        self.scantype='enum4linux'
        self.targets = targets
        self.port = '445'
        self.commandline = lambda scheme, target, port:\
            "enum4linux -u '%s\\%s' -p '%s' %s 2>output/err.%s | tee output/out.enum.%s"%\
            (domain,user,password, target, target, target)
        self.output_filename_pattern = 'out\.enum\.([0-9.]+)'



class Ffuf(ScraperJob):
    def __init__(self, targets, processes=4, port='80'):
        super().__init__()
        self.targets = targets
        self.path = 'results'
        self.scantype='ffuf'
        self.targets = targets
        self.port = port
        self.output_filename_pattern = 'out\.ffuf\.([0-9.]+)'
    
    def scan(self, scheme='http'):
        self.scheme = scheme
        if self.port == '443':
            self.scheme = 'https'
        os.chdir(self.path)
        try:
            os.mkdir(self.ident)
        except:
            pass
        os.chdir(self.ident)
        os.mkdir('output')

        targetqueue = Queue(maxsize = 8)
        processes = []
        def enumtask(target):
            targetspec = scheme + '://'
            targetspec += target
            if self.port:
                targetspec += ':%s'%self.port
            targetspec += '/FUZZ'
            targetqueue.put(target)

            # replace the quickhits with your wordlist of choice
            c="ffuf -mc 200,204,307,418 -w ../../resources/quickhits.txt -u %s -o output/out.ffuf.%s 2>output/err.%s"%(targetspec, target, target)
            sys.stderr.write('%s\n'%c)
            os.system(c)
            targetqueue.get()
        for t in self.targets:
            p = Process(target = lambda: enumtask(t))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        self.postprocess()
        sys.stderr.write("ffuf task done\n")

    def postprocess(self):
        results = []
        re_filename = re.compile('out\.ffuf\.([0-9.]+)')
        for x in os.listdir('output'):
            m = re_filename.match(x)
            if m and m.groups():
                ip = m.groups()[0]
                fuf = json.loads(open('output/%s'%x,'r').read())
                results.append({'host': ip, 'scantype': 'ffuf', 'port': self.port, 'output': fuf})
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': 'ffuf',
                 'jobid': self.ident,
                 'target': self.targets,
                 'port': self.port }
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()
        
    
class Snmpwalk(ScraperJob):
    def __init__(self, targets, processes=4):
        super().__init__()
        self.path = 'results'
        self.scantype='snmpwalk'
        self.targets = targets
        self.port = '161'
        self.commandline = lambda scheme, target, port: \
            "snmpwalk -c public -v1 %s 2>output/err.%s | tee output/out.snmpwalk.%s"%\
            (target, target, target)
        self.output_filename_pattern = 'out\.snmpwalk\.([0-9.]+)'
    
        
            
    
class Bluekeep(ScraperJob):
    def __init__(self, targets, processes=4):
        super().__init__()
        self.targets = targets
        self.path = 'results'
        self.scantype='bluekeep'
        self.targets = targets
    
    def scan(self):
        self.port = '3389'
        os.chdir(self.path)
        try:
            os.mkdir(self.ident)
        except:
            pass
        os.chdir(self.ident)

        targetqueue = Queue(maxsize = 8)
        os.system('../../scanners/blue.sh %s |tee output.txt'%' '.join(self.targets))
        self.postprocess()
        sys.stderr.write("bluekeep task done\n")

    def postprocess(self):
        results = []
        #line looks like:
        # [*] 192.168.9.5:3389 - Cannot reliably check exploitability.
        re_shit = re.compile('\[.\]\s([^:]*):[0-9]+\s+-\s(.*)')
        for line in open('output.txt','r').readlines():
            m = re_shit.match(line.strip())
            if m and m.groups():
                results.append({'host': m.groups()[0], 'scantype': 'bluekeep', 'status': m.groups()[1], 'port': '3389'})
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': 'bluekeep',
                 'jobid': self.ident,
                 'target': self.targets,
                 'port': self.port }
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()

class Ms17_010(ScraperJob):
    def __init__(self, targets, processes=4):
        super().__init__()
        self.targets = targets
        self.path = 'results'
        self.scantype='ms17_010'
        self.targets = targets
    
    def scan(self):
        self.port = '445'
        os.chdir(self.path)
        try:
            os.mkdir(self.ident)
        except:
            pass
        os.chdir(self.ident)

        targetqueue = Queue(maxsize = 8)
        os.system('../../scanners/ms17_010.sh %s > output.txt'%' '.join(self.targets))
        self.postprocess()
        sys.stderr.write("ms17_010 task done\n")

    def postprocess(self):
        results = []
        #line looks like:
        # [*] 192.168.9.5:3389 - Cannot reliably check exploitability.
        re_shit = re.compile('\[.\]\s([^:]*):[0-9]+\s+-\s(.*)')
        hostresults = collections.defaultdict(list)
        for line in open('output.txt','r').readlines():
            m = re_shit.match(line.strip())
            if m and m.groups():
                hostresults[m.groups()[0]].append(m.groups()[1])
        for key in hostresults.keys():
            results.append({'host': key, 'scantype': 'ms17_010', 'status': ''.join(hostresults[key]), 'port': self.port})
            
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': 'ms17_010',
                 'jobid': self.ident,
                 'target': self.targets,
                 'port': self.port }
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()


class Ms12_020(ScraperJob):
    def __init__(self, targets, processes=4):
        super().__init__()
        self.targets = targets
        self.path = 'results'
        self.scantype='ms12_020'
        self.targets = targets
    
    def scan(self):
        self.port = '3389'
        os.chdir(self.path)
        try:
            os.mkdir(self.ident)
        except:
            pass
        os.chdir(self.ident)

        targetqueue = Queue(maxsize = 8)
        os.system('../../scanners/ms12_020.sh %s > output.txt'%' '.join(self.targets))
        self.postprocess()
        sys.stderr.write("ms12_020 task done\n")

    def postprocess(self):
        results = []
        #line looks like:
        # [*] 192.168.9.5:3389 - Cannot reliably check exploitability.
        re_shit = re.compile('\[.\]\s([^:]*):[0-9]+\s+-\s(.*)')
        hostresults = collections.defaultdict(list)
        for line in open('output.txt','r').readlines():
            m = re_shit.match(line.strip())
            if m and m.groups():
                hostresults[m.groups()[0]].append(m.groups()[1])
        for key in hostresults.keys():
            results.append({'host': key, 'scantype': 'ms12_020', 'status': ''.join(hostresults[key]), 'port': self.port})
            
        f = open('results.json','w')
        f.write(json.dumps(results, indent=4, sort_keys=True))
        meta = { 'scantype': 'ms12_020',
                 'jobid': self.ident,
                 'target': self.targets,
                 'port': self.port }
        open('info.json','w').write(json.dumps(meta, indent=4,sort_keys=True))
        f.close()
        
