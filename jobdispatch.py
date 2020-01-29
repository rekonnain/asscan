#!/usr/bin/env python3

from multiprocessing import Process, Queue
import json
import notes
from scanners import *
from scrapers import *
from results import *
import re
from os.path import join
import collections
import ipaddress
re_uuid = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)


# queues for tasks of different kinds. The maxsize parameter determines
# how many tasks can be active in parallel at any given time
massqueue = Queue(maxsize = 1)
masscount = 0
nmapqueue = Queue(maxsize = 4)
nmapcount = 0
vulnqueue = Queue(maxsize = 16)
vulncount = 0
scraperqueue = Queue(maxsize = 8)
scrapercount = 0

alljobs = {}


def forkjob(job, queue):
    def task():
        sys.stderr.write("Queueing %s\n"%job.ident)
        queue.put(job.ident)
        alljobs[job.ident] = job
        job.scan()
        del alljobs[job.ident]
        x=queue.get()
        sys.stderr.write('Job %s done\n'%job.ident)
        if job.posthook:
            sys.stderr.write('Executing post hook for job %s\n'%job.ident)
            job.posthook()
        sys.stderr.write("Removed %s from queue\n"%x)
        sys.stderr.write("Queue length %d\n"%queue.qsize())
    p = Process(target = task)
    p.start()

def get_scans():
    r = Results()
    r.read_all('results')
    return {'scans': sorted(r.scans, key=lambda x:x['target'])}

def get_results_for_ip(ip):
    r = Results()
    r.read_all('results')
    result = {}
    if ip in r.hosts.keys():
        return {ip: r.hosts[ip]}
    else:
        return {}

def get_results_by_port(port):
    r = Results()
    r.read_all()
    return r.by_port(port)

def get_filtered_results(filters):
    prefix = filters['prefix']
    port = filters['port']
    service = filters['service']
    vulns = filters['vulns']
    screenshots = filters['screenshots']
    notes = filters['notes']
    r = Results()
    r.read_all('results')
    filtered = r.hosts
    sys.stderr.write('count all=%d\n'%(len(filtered.keys())))
    if prefix and len(prefix) > 0:
        if not prefix[-1] == '.':
            prefix += '.'
        filtered = filter_by_prefix(filtered, prefix)
        sys.stderr.write('count prefix=%d\n'%(len(filtered.keys())))
    if port and len(port) > 0:
        filtered = filter_by_port(filtered, port)
        sys.stderr.write('count port=%d\n'%(len(filtered.keys())))
    if service and len(service) > 0:
        filtered = filter_by_service(filtered, service)
        sys.stderr.write('count service=%d\n'%(len(filtered.keys())))
    if vulns and vulns == 'true':
        filtered = filter_by_vulns(filtered)
        sys.stderr.write('count vulns=%d\n'%(len(filtered.keys())))
    if screenshots and screenshots == 'true':
        filtered = filter_by_screenshots(filtered)
        sys.stderr.write('count screenshots=%d\n'%(len(filtered.keys())))
    if notes and notes == 'true':
        filtered = filter_by_having_notes(filtered)
        sys.stderr.write('count notes=%d\n'%(len(filtered.keys())))
    sys.stderr.write('count final=%d\n'%(len(filtered.keys())))
    return {'ips':list(filtered.keys())}

def get_all_results():
    r = Results()
    r.read_all('results')
    return r.hosts

def list_ips():
    r = Results()
    r.read_all('results')
    return {'ips':sorted(list(r.hosts.keys()))}

def get_attachment(pathcomponents):
    if re_uuid.match(pathcomponents[0]): # some scans save files, this returns them
        filepath = join('results', *pathcomponents)
        if filepath.endswith('.png'):
            self.set_header('content-type', 'image/png')
            return open(filepath,'rb').read()
        if filepath.endswith('.jpg'):
            self.set_header('content-type', 'image/jpg')
            return open(filepath,'rb').read()
        else:
            self.set_header('content-type', 'text/plain')
            return open(filepath,'rb').read()
    else:
        return {"status": "not ok"} # what
    
    

# TODO, keep counters on jobs waiting on the queue, these
# counters only tell if the queue is full or not
def get_jobs_overview():
    return {'nmap': nmapqueue.qsize(),
            'masscan': massqueue.qsize(),
            'scrapers': scraperqueue.qsize(),
            'vuln': vulnqueue.qsize()}

# TODO is this even in use currently?
def get_jobs_status():
    status = {}
    for key in alljobs.keys():
        status[key] = alljobs[key].status
    return status



def forkjobs(jobspec):
    print(json.dumps(jobspec, indent=4, sort_keys=True))
    scantypes = jobspec['scantypes'] if 'scantypes' in jobspec else []
    foundonly = jobspec['found_only'] if 'found_only' in jobspec else False
    if foundonly == 'false' or foundonly == '0': # how stringly
        foundonly = False
    target = jobspec['target'] if 'target' in jobspec else None
    mask = jobspec['mask'] if 'mask' in jobspec else None
    maxmask = jobspec['maxmask'] if 'maxmask' in jobspec else None
    vncpassword = jobspec['vncpassword'] if 'vncpassword' in jobspec else ''
    username = jobspec['username'] if 'username' in jobspec else None
    domain = jobspec['domain'] if 'domain' in jobspec else None
    password = jobspec['password'] if 'password' in jobspec else None
    hostkeys = None
    if ',' in target:
        hostkeys = target.replace(' ','').split(',')

    massjobs = []
        
    # When submitting multiple job types in the same request and masscan is one of
    # the scan types, we first want to perform the masscan and only after that, the
    # other scan types, because we implictly perform other scans only against already
    # discovered hosts.
    # As the "already discovered" is handled here, we need to postpone finding out
    # which hosts are discovered until the masscan is done...
    posthook = None

    if 'masscan' in scantypes and len(scantypes) > 1:
        othertypes = scantypes[:]
        othertypes.remove('masscan')
        otherjobspec = jobspec.copy()
        otherjobspec['scantypes'] = othertypes
        otherjobspec['found_only'] = 'true'
        scantypes = ['masscan']
        posthook = lambda: forkjobs(otherjobspec)

    
    if not target or not mask:
        return{'status': 'fuck off',
               'reason': 'target or mask missing'}

    for typ in scantypes:
        if typ == 'masscan':
            targetspec = [target + '/' + mask]
            jobids = []
            port = jobspec['port'] if 'port' in jobspec else None

            # split a netmask N scan into smaller scans of mask M
            # 10.0.0.0/8 with submask /9 --> two scans
            # /16 scans are kinda ok with /19 scans, for example
            if maxmask: 
                targetspec = []
                for x in ipaddress.ip_network(target + '/' + mask).subnets(new_prefix = int(maxmask)):
                    targetspec.append(str(x.network_address) + '/' + maxmask)
            for t in targetspec:
                if port and len(port) > 0: # custom port
                    job = Masscan(t, ports = port.replace(' ',''))
                else: # default port list, see the masscan class
                    job = Masscan(t)
                massjobs.append(job)
                #forkjob(job, massqueue)
                jobids.append(job.ident)
        elif typ == 'nmap':
            if foundonly: # only scan hosts found earlier with masscan
                r = Results()
                r.read_all('results')
                hosts = filter_by_network(r.hosts, target, mask)
                hosts = filter_by_missing_scan(hosts, 'nmap')
                hostkeys = list(hosts.keys())
                n = 32
                hostkeylists = [hostkeys[i * n:(i + 1) * n] for i in range((len(hostkeys) + n - 1) // n )]
                jobids = []
                for kl in hostkeylists:
                    job = Nmap(kl)
                    forkjob(job, nmapqueue)
                    jobids.append(job.ident)
            else:
                targetspec = [target + '/' + mask]
                jobids = []
                if maxmask:
                    targetspec = []
                    for x in ipaddress.ip_network(target + '/' + mask).subnets(new_prefix = int(maxmask)):
                        targetspec.append(str(x.network_address) + '/' + maxmask)
                for t in targetspec:
                    job = Nmap(t)
                    forkjob(job, nmapqueue)
                    jobids.append(job.ident)
        elif typ == 'nmap-udp': # TODO missing the foundonly flag handling!
            udp = True
            targetspec = None
            prefix = jobspec['prefix'] if 'prefix' in jobspec else None
            job = Nmap(targetspec, udp=True)
            forkjob(job, nmapqueue)
        elif typ == 'smbvuln': # check if this still works. OTOH ms17-010 has its own checker now
            targetspec = target + '/' + mask
            job = SmbVuln(targetspec)
            forkjob(job, vulnqueue)
        elif typ == 'webscreenshot':
            # Fetch results for target subnet, only screenshot those with open ports
            port = jobspec['port'] if 'port' in jobspec else '80'
            scheme = jobspec['scheme'] if 'scheme' in jobspec else 'http'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly: # better have this set, or hardcode
                hosts = filter_by_port(hosts, port)
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            job = WebScreenshot(list(hosts.keys()), scheme, port)
            forkjob(job, scraperqueue)
        elif typ == 'rdpscreenshot':
            port = jobspec['port'] if 'port' in jobspec else '3389'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                hosts = filter_by_port(hosts, port)
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            print('hostkeys %s'%str(hostkeys))
            job = RdpScreenshot(hostkeys)
            forkjob(job, scraperqueue)
        elif typ == 'vncscreenshot':
            # Fetch results for target subnet, only screenshot those with open ports
            port = jobspec['port'] if 'port' in jobspec else '5901'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                hosts = filter_by_port(hosts, port)
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            print('hostkeys %s'%str(hostkeys))
            job = VncScreenshot(hostkeys, port=port, password=vncpassword)
            forkjob(job, scraperqueue)
        elif typ == 'enum4linux':
            # Fetch results for target subnet, only screenshot those with open ports
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hostkeys = []
            hosts = filter_by_network(hosts, target, mask)
            print('filtered: %s'%str(hosts.keys()))
            if foundonly:
                hosts = filter_by_port(hosts, '445') # should this be 139 or 445?
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            job = Enum4Linux(hostkeys)
            forkjob(job, scraperqueue)
        elif typ == 'snmpwalk':
            # Fetch results for target subnet, only screenshot those with open ports
            prefix = jobspec['prefix'] if 'prefix' in jobspec else None
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            job = Snmpwalk(hostkeys)
            forkjob(job, scraperqueue)
        elif typ == 'ffuf':
            # Fetch results for target subnet, only screenshot those with open ports
            port = jobspec['port'] if 'port' in jobspec else '80'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                sys.stderr.write('0: %s\n'%str(list(hosts.keys())))
                hosts = filter_by_port(hosts, port)
                sys.stderr.write('1: %s\n'%str(list(hosts.keys())))
            hostkeys = list(hosts.keys())
            job = Ffuf(hostkeys, port=port)
            forkjob(job, scraperqueue)
        elif typ == 'bluekeep':
            # Fetch results for target subnet, only screenshot those with open ports
            port = '3389'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                #sys.stderr.write('0: %s\n'%str(list(hosts.keys())))
                hosts = filter_by_port(hosts, port)
                sys.stderr.write('1: %s\n'%str(list(hosts.keys())))
            hostkeys = list(hosts.keys())
            n = 32
            hostkeylists = [hostkeys[i * n:(i + 1) * n] for i in range((len(hostkeys) + n - 1) // n )]
            jobids = []
            for kl in hostkeylists:
                job = Bluekeep(kl)
                forkjob(job, scraperqueue)
                jobids.append(job.ident)
        elif typ == 'ms17_010':
            # Fetch results for target subnet, only screenshot those with open ports
            port = '445'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                sys.stderr.write('0: %s\n'%str(list(hosts.keys())))
                hosts = filter_by_port(hosts, port)
                sys.stderr.write('1: %s\n'%str(list(hosts.keys())))
            hostkeys = list(hosts.keys())
            job = Ms17_010(hostkeys)
            forkjob(job, scraperqueue)
        elif typ == 'sleep':
            job = SleepJob()
            forkjob(job, nmapqueue)
        else:
            pass

    if len(massjobs) > 0:
        massjobs[-1].posthook = posthook
        for job in massjobs:
            forkjob(job, massqueue)
    return {'status': 'ok'} # TODO, return some info of queued jobs

    
