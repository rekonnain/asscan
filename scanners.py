#!/usr/bin/env python3

import subprocess
import uuid
import sys
import json
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import time

# superclass for scan jobs
# supports running something as a subprocess
class Job:
    def __init__(self):
        self.ident = str(uuid.uuid4())
        self.state = 'init'
        self.cmdline = 'n/a'
        self.targets = []
        self.scantype = 'n/a'
        self.posthook = None
        self.timeout = 900

    def run(self, argv):
        sys.stderr.write("Starting job: %s\n"%' '.join(argv))
        print(str(argv))
        self.cmdline = ' '.join(argv)
        p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.state = 'running'
        self.err = p.stderr.read()
        self.output = p.stdout.read()
        sys.stderr.write("Done running: %s\n"%' '.join(argv))
        sys.stderr.write(str(p.stderr.read()))
        self.state = 'done'

    def describe(self):
        return {'cmdline': self.cmdline,\
                'targets': self.targets,\
                'type': self.scantype,\
                'ident': self.ident}

    # override if necessary
    def contains_target(self, target):
        return target  in self.targets

# nop scan job to test queues
class SleepJob(Job):
    def scan(self):
        for x in range(20):
            time.sleep(0.5)
            sys.stderr.write("sleeping %s\n"%(self.ident))
        sys.stderr.write("done sleeping %s\n"%(self.ident))
        


# parent class for scan jobs
class ScanJob(Job):
    def load_file(self, filename):
        self.resultsfile = filename
        self.ident = self.resultsfile.split('/')[1].split('.')[0]
        self.timestamp = os.stat(self.resultsfile).st_ctime
        self.parse_nmap()
    
    def __init__(self):
        super().__init__()
        self.hosts = defaultdict(dict)
        self.resultsfile = os.path.join('results',self.ident,'output.xml')

    # parses scan results from an xml file written by either nmap or masscan
    # they are the same, except masscan can have multiple entries for a single host
    def parse_nmap(self):
        tree = None
        root = None
        metadata = {}
        try:
            tree = ET.parse(self.resultsfile)
            root = tree.getroot() # 'nmaprun'
        except:
            # the file doesn't have the root in these cases:
            # 1. scan is still going on, the file is created but not fully written into
            # 2. scan was killed or incomplete or something
            return
        ismass = root.attrib['scanner'] == 'masscan' # see later why we need this
        hosts={} # collects all host entries
        host={} # placeholder for single host

        # iterate hosts
        for hostNode in root.iter('host'):
            for anode in hostNode.iter('address'):
                atts = anode.attrib
                if 'addr' in atts and 'addrtype' in atts:
                    if atts['addrtype'] == 'ipv4':
                        host['ipv4'] = atts['addr']
                    elif atts['addrtype'] == 'ipv6':
                        host['ipv6'] == atts['addr']
                    elif atts['addrtype'] == 'mac':
                        host['mac'] = atts['addr']
                    if 'vendor' in atts:
                        host['vendor'] = atts['vendor']
            host['ports'] = []
            host['osmatches'] = []
            for ports in hostNode.findall('ports'):
                for pnode in ports.iter('port'):
                    pdict = {}
                    atts = pnode.attrib
                    portid = atts['portid']
                    pdict['port'] = portid
                    pdict['protocol'] = atts['protocol']
                    try: # Port state
                        stateelem = pnode.find('state')
                        pdict['state'] = stateelem.attrib['state']
                        pdict['reason'] = stateelem.attrib['reason']
                        pdict['ttl'] = stateelem.attrib['reason_ttl']
                    except:
                        pass
                    if ismass:
                        pdict['state'] = 'open'
                    try: # Service element, nmap only
                        selem = pnode.find('service')
                        pdict['service'] = selem.attrib['name']
                        if 'extrainfo' in selem.attrib:
                            pdict['serviceinfo'] = selem.attrib['extrainfo']
                    except:
                        pass
                    try: # Script scans, nmap only
                        scripts={}
                        for selem in pnode.findall('script'):
                            scripts[selem.attrib['id']] = selem.attrib['output']
                        pdict.update(scripts)
                    except:
                        pass
                    if 'state' in pdict:
                        if pdict['state'] == 'open':
                            host['ports'].append(pdict)
                    else:
                        host['ports'].append(pdict)
            host['osmatches'] = []
            host['jobid'] = self.ident
            host['scantype'] = root.attrib['scanner']
            host['cmdline'] = root.attrib['args'] if 'args' in root.attrib else ''
            host['scantime'] = root.attrib['startstr'] if 'startstr' in root.attrib else ''
            osNode = hostNode.find('os')
            if osNode:
                for osmatch in osNode.findall('osmatch'):
                    host['osmatches'].append({'name': osmatch.attrib['name'],
                                              'accuracy': osmatch.attrib['accuracy']})
            key = host['ipv4']
            host['timestamp'] = self.timestamp
            # script scans
            hostscriptnode = hostNode.find('hostscript')
            if hostscriptnode:
                scripts={}
                for selem in hostscriptnode.findall('script'):
                    scripts[selem.attrib['id']] = selem.attrib['output']
                host['scripts']=scripts
            if host['ipv4'] in self.hosts.keys(): # host exists, only update the ports list
                self.hosts[key]['ports'] += host['ports']
                o = set(self.hosts[key]['osmatches'])
                o.update(host['osmatches'])
                self.hosts[key]['osmatches'] = list(o)
            else:
                self.hosts[key] = host
            host = {}

    def to_json(self):
        o = {'id': self.ident,
             'hosts': self.hosts}
        return json.dumps(o, indent=4, sort_keys=True)

    def from_json(self, j):
        obj = json.loads(j)
        self.ident = obj['id']
        self.hosts = obj['hosts']

class Masscan(ScanJob):
    def __init__(self, target, ports='1,3,7,9,13,17,19,21-23,25-26,37,53,79-82,88,100,106,110-111,113,119,135,139,143-144,179,199,254-255,280,311,389,427,443-445,464-465,497,513-515,543-544,548,554,587,593,625,631,636,646,787,808,873,902,990,993,995,1000,1022,1024-1033,1035-1041,1044,1048-1050,1053-1054,1056,1058-1059,1064-1066,1069,1071,1074,1080,1110,1234,1433,1494,1521,1720,1723,1755,1761,1801,1900,1935,1998,2000-2003,2005,2049,2103,2105,2107,2121,2161,2301,2383,2401,2601,2717,2869,2967,3000-3001,3128,3268,3306,3389,3689-3690,3703,3986,4000-4001,4045,4899,5000-5001,5003,5009,5050-5051,5060,5101,5120,5190,5357,5432,5555,5631,5666,5800,5900-5901,6000-6002,6004,6112,6646,6666,7000,7070,7937-7938,8000,8002,8008-8010,8031,8080-8081,8443,8888,9000-9001,9090,9100,9102,9999-10001,10010,25565,32768,32771,49152-49157,50000'):
        super().__init__()
        self.target = target
        if self.target.endswith('/32'):
            self.target = self.target.replace('/32','')
        self.ports = ports

    def scan(self):
        sys.stderr.write("Starting masscan on %s, jobid %s\n"%(self.target, self.ident))
        os.mkdir(os.path.join('results', self.ident))
        args = ['masscan', '-p'+self.ports, '--rate=20000', '-oX', self.resultsfile, self.target]
        self.cmdline = ' '.join(args)
        super().run(args)
        meta = { 'scantype': 'masscan',
                 'jobid': self.ident,
                 'target': self.target,
                 'ports': self.ports }
        open(os.path.join('results',self.ident,'info.json'),'w').write(json.dumps(meta, indent=4,sort_keys=True))
        sys.stderr.write("Masscan done on %s, jobid %s\n"%(self.target, self.ident))
        
class Nmap(ScanJob):
    def __init__(self, target, script='vulners,default', portspec=None, udp=False):
        super().__init__()
        self.target = target
        self.script = script
        self.portspec = portspec
        self.udp = udp

    def scan(self):
        sys.stderr.write("Starting nmap on %s, jobid %s\n"%(self.target, self.ident))
        os.mkdir(os.path.join('results', self.ident))
        args = ['nmap', '-oX', self.resultsfile, '--script', 'vulners,default']
        if self.udp:
            args.append('-sU')
        else:
            args+=['-T4', '-A']
        if self.script:
            args.append('--script=%s'%self.script)
        if self.portspec:
            args.append('-p%s'%self.portspec)
        if type(self.target) == list:
            args.append('-Pn') # don't ping if we know which hosts to scan
            args += self.target
        else:
            args.append(self.target)
        self.cmdline = ' '.join(args)
        #super().run(args)
        os.system(self.cmdline)
        meta = { 'scantype': 'nmap',
                 'jobid': self.ident,
                 'target': self.target}
        open(os.path.join('results',self.ident,'info.json'),'w').write(json.dumps(meta, indent=4,sort_keys=True))
        sys.stderr.write("nmap done on %s, jobid %s\n"%(self.target, self.ident))

if __name__=='__main__':
    s=ScanJob()
    s.load_file(sys.argv[1])
    print(json.dumps(s.hosts, indent=4, sort_keys=True))
