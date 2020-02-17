#!/usr/bin/env python3

from os import listdir
from os.path import join, isfile, isdir
import json, sys
from scanners import ScanJob
from collections import defaultdict
import notes
import ipaddress
import os
import jobdispatch as jd

# functions to filter a results dict by criteria
def filter_by_port(hosts, port):
    result = defaultdict(list)
    for key in hosts.keys():
        for scan in hosts[key]:
            if str(port) in [x['port'] for x in scan['ports']]:
                result[key].append(scan)
    return result

# prefix is a left part of an ip address, eg 192.168
def filter_by_prefix(hosts, prefix):
    result = {}
    for key in hosts.keys():
        if key.startswith(prefix):
            result[key] = hosts[key]
    return result

# makes sense only for nmap scans as the script part creates the service info
def filter_by_service(hosts, service):
    result = defaultdict(list)
    for key in hosts.keys():
        for scan in hosts[key]:
            for port in scan['ports']:
                if 'service' in port and port['service'].startswith(service):
                    result[key].append(scan)
    return result

def filter_by_network(hosts, address, mask):
    if mask == '32' and len(address.split('.')) == 4:
        return {address: hosts[address]}
    filtered = {}
    network = ipaddress.ip_network('%s/%s'%(address,mask))
    for key in hosts.keys():
        if ipaddress.ip_address(key) in network:
            filtered[key] = hosts[key]
    return filtered

def filter_by_having_notes(hosts):
    noted = notes.hostswithcomments()
    filtered = {}
    for key in hosts.keys():
        if key in noted:
            filtered[key] = hosts[key]
    return filtered
        
# useful but not exposed to the UI, I think
# consider having a checkbox for this in the UI
def filter_by_missing_scan(hosts, scantype):
    filtered = {}
    for key in hosts.keys():
        if not scantype in map(lambda x:x['scantype'], hosts[key]):
            filtered[key] = hosts[key]
    return filtered


# horrendous hack
def filter_by_bluekeep(hosts):
    filtered = {}
    for key in hosts.keys():
        for scan in hosts[key]:
            if scan['scantype'] == 'bluekeep'\
                and 'target is vulnerable' in scan['ports'][0]['status']:
                filtered[key] = hosts[key]
                #sys.stderr.write(scan['ports'][0]['status'] + '\n')
    return filtered

def filter_by_ms17010(hosts):
    filtered = {}
    for key in hosts.keys():
        for scan in hosts[key]:
            if scan['scantype'] == 'ms17_010'\
                 and 'Host is likely VULNERABLE' in scan['ports'][0]['status']:
                filtered[key] = hosts[key]
                #sys.stderr.write(scan['ports'][0]['status'] + '\n')
    return filtered

def filter_by_vulns(hosts):
    filtered = filter_by_ms17010(hosts)
    filtered.update(filter_by_bluekeep(hosts))
    return filtered
    
def filter_by_screenshots(hosts):
    filtered = {}
    for key in hosts.keys():
        for scan in hosts[key]:
            if 'screenshot' in scan['scantype']:
                filtered[key] = hosts[key]
    return filtered

def get_results(args, filters={}):
    if args[0] == 'ip': # single result by ip, /results/ip/192.168.0.1
        ip = args[1]
        return get_results_for_ip(ip)
    elif args[0] == 'port':
        port = args[1]
        return get_results_by_port(port)
    elif args[0] == 'filter':
        #sys.stderr.write('filtering: prefix=%s port=%s service=%s vulns=%s screenshots=%s\n'%(str(prefix), str(port), str(service), str(vulns), str(screenshots)))
        return get_filtered_results(filters)
    elif args[0] == 'all':
        r = Results()
        r.read_all('results')
        return r.hosts
    elif args[0] == 'networks': # i don't think this is used currently
        r = Results()
        r.read_all('results')
        counts = collections.defaultdict(int)
        for key in r.hosts.keys():
            k = '.'.join(key.split('.')[:2])
            counts[k] += 1
        return dict(counts)
    elif args[0] == 'ips':
        r = Results()
        r.read_all('results')
        return {'ips':sorted(list(r.hosts.keys()))}
    elif re_uuid.match(args[0]): # some scans save files, this returns them
        filepath = join('results', *args)
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
    r.read_all('results')
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


class Results:
    def __init__(self):
        self.hosts = defaultdict(list)
        self.scans = [] # masscans and nmaps

    # reads all files in the given path.
    # for backwards compatibility, a nmap/masscan results file can be in the results dir
    # as [uuid].xml
    # everything else should be either [uuid]/output.xml for nmap/masscan
    # and [uuid]/results.json for all other types
    def read_all(self, path):
        files = [x for x in listdir(path) if isfile(join(path, x)) and x.endswith('.xml')]
        directories = [x for x in listdir(path) if isdir(join(path, x))]
        for f in files:
            j = ScanJob()
            j.load_file(join(path,f))
            for key in j.hosts.keys():
                #print(h)
                self.hosts[key].append(j.hosts[key])
        for d in directories:
            rfile = join(path, d, 'results.json')
            if isfile(rfile):
                r = json.loads(open(rfile,'r').read())
                for entry in r:
                    host = entry['host']
                    port = entry['port']
                    fname = join(path, d, entry['file']) if 'file' in entry else ''
                    scantype = entry['scantype']
                    if scantype == 'ffuf':
                        obj = {'ipv4': host, 'scantype': scantype, 'ports': [{'port': port, 'file': fname, 'results': entry['output']['results']}]}
                    if scantype == 'bluekeep' or scantype == 'ms17_010':
                        obj = {'ipv4': host, 'scantype': scantype, 'ports': [{'port': port, 'status': entry['status']}]}
                    elif fname == '' or os.stat(fname).st_size == 0:
                        continue
                    else:
                        obj = {'ipv4': host, 'scantype': scantype, 'ports': [{'port': port, 'file': fname}]}
                        
                    self.hosts[host].append(obj)
            elif isfile(join(path,d, 'output.xml')):
                j = ScanJob()
                j.load_file(join(path,d, 'output.xml'))
                for key in j.hosts.keys():
                    self.hosts[key].append(j.hosts[key])
            infoname = join(path, d, 'info.json')
            if isfile(infoname):
                info = json.loads(open(infoname, 'r').read())
                if info['scantype'] in ['nmap', 'masscan']:
                    try:
                        net = ipaddress.ip_network(info['target']) #just check if it's valid
                        self.scans.append(info)
                    except:
                        pass

    def by_ip(self, ip):
        return self.hosts[ip]

    def by_port(self, port):
        return filter_by_port(self.hosts, port)

if __name__=='__main__':
    r = Results()
    r.read_all(sys.argv[1])
    print(json.dumps(r.hosts, indent=4, sort_keys=True))
