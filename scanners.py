#!/usr/bin/env python3

from subprocess import *
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

    def run(self, argv):
        sys.stderr.write("Starting job: %s\n"%' '.join(argv))
        print(str(argv))
        self.cmdline = ' '.join(argv)
        p = Popen(argv, stdout=PIPE, stderr=PIPE)
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
    def __init__(self, target, ports='21-25,53,80-88,111,139,143,443,445,8080-8088,8888-8890,1403,3389,3306,5900-5910,27017-27019,5984,5985,5986,47001,6667-6670'):
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
    def __init__(self, target, script=None, portspec=None, udp=False):
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

class SmbVuln(ScanJob):
    def __init__(self, target):
        super().__init__()
        self.target = target

    def scan(self):
        super().run(['nmap', '-T4', '-A', '-p139,445', '--script=smb*vuln*', '-oX', self.resultsfile, self.target])

if __name__=='__main__':
    s=ScanJob()
    s.load_file(sys.argv[1])
    print(json.dumps(s.hosts, indent=4, sort_keys=True))
