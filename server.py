#!/usr/bin/env python3
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode
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
from log import log
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

class ScansHandler(tornado.web.RequestHandler):
    def get(self):
        # Returns all past scans
        r=Results()
        r.read_all('results')
        self.write({'scans': sorted(r.scans, key=lambda x:x['target'])})

class NotesHandler(tornado.web.RequestHandler):
    def get(self, shit):
        args = shit.split('/')
        if len(args) == 2 and args[0] == 'ip':
            self.write(notes.notesforhost(args[1]))
        else:
            self.write({})

    def post(self, dummy):
        x = json_decode(self.request.body)
        for key, val in x.items():
            notes.savenote(key,val)
        self.write({})

    def delete(self, args):
        ip = args.split('/')[0]
        notes.deletenote(ip)
        self.write({})

class ResultsHandler(tornado.web.RequestHandler):
    def get(self, shit):
        # Returns results from all scans
        # The web UI only uses the /filter? api
        args = shit.split('/')

        if args[0] == 'ip': # single result by ip, /results/ip/192.168.0.1
            ip = args[1]
            r = Results()
            r.read_all('results')
            result = {}
            if ip in r.hosts.keys():
                self.write({ip: r.hosts[ip]})
            else:
                self.write({})
        elif args[0] == 'port':
            port = args[1]
            r = Results()
            r.read_all('results')
            self.write(r.by_port(port))
        elif args[0] == 'filter':
            prefix = self.get_query_argument('prefix', None)
            port = self.get_query_argument('port', None)
            service = self.get_query_argument('service', None)
            vulns = self.get_query_argument('vulns', None)
            screenshots = self.get_query_argument('screenshots', None)
            notes = self.get_query_argument('notes', None)
            content = self.get_query_argument('content', None)
            sys.stderr.write('filtering: prefix=%s port=%s service=%s vulns=%s screenshots=%s content=%s\n'%(str(prefix), str(port), str(service), str(vulns), str(screenshots), str(content)))
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
            if content and len(content) > 0 and content != 'undefined':
                filtered = filter_by_content(filtered, content)
                sys.stderr.write('count content=%d\n'%len(filtered.keys()))
            sys.stderr.write('count final=%d\n'%(len(filtered.keys())))
            self.write({'ips':sorted_addresses(filtered.keys())})
        elif args[0] == 'all':
            r = Results()
            r.read_all('results')
            self.write(r.hosts)
        elif args[0] == 'networks': # i don't think this is used currently
            r = Results()
            r.read_all('results')
            counts = collections.defaultdict(int)
            for key in r.hosts.keys():
                k = '.'.join(key.split('.')[:2])
                counts[k] += 1
            self.write(dict(counts))
        elif args[0] == 'ips':
            r = Results()
            r.read_all('results')
            self.write({'ips':sorted(list(r.hosts.keys()))})
        elif re_uuid.match(args[0]): # some scans save files, this returns them
            filepath = join('results', *args)
            if filepath.endswith('.png'):
                self.set_header('content-type', 'image/png')
                self.write(open(filepath,'rb').read())
            if filepath.endswith('.jpg'):
                self.set_header('content-type', 'image/jpg')
                self.write(open(filepath,'rb').read())
            else:
                self.set_header('content-type', 'text/plain')
                self.write(open(filepath,'rb').read())
        else:
            self.write({"status": "not ok"}) # what

    
            
# information on current scan jobs
class JobsHandler(tornado.web.RequestHandler):
    def get(self, shit):
        args = shit.split('/')
        if args[0] == 'overview':
            jobs = {'nmap': nmapqueue.qsize(),
                    'masscan': massqueue.qsize(),
                    'scrapers': scraperqueue.qsize(),
                    'vuln': vulnqueue.qsize()}
            self.write(jobs)
        elif args[0] == 'status':
            status = {}
            for key in alljobs.keys():
                status[key] = alljobs[key].status
            self.write(status)
        else:
            self.write({'error': 'fuck off'})
            

    # submits a new scan job
    def post(self, dummy = None):
        jobspec = json_decode(self.request.body)
        self.write(forkjobs(jobspec))

def split(lst, n):
    return [lst[i * n:(i + 1) * n] for i in range((len(lst) + n - 1) // n )]
        
def forkjobs(jobspec):
    print(json.dumps(jobspec, indent=4, sort_keys=True))
    scantypes = jobspec['scantypes'] if 'scantypes' in jobspec else []
    foundonly = jobspec['onlyfound'] if 'onlyfound' in jobspec else False
    if foundonly == 'false' or foundonly == '0': # how stringly
        foundonly = False
    target = jobspec['target'] if 'target' in jobspec else None
    mask = jobspec['mask'] if 'mask' in jobspec else None
    maxmask = jobspec['maxmask'] if 'maxmask' in jobspec else None
    vncpassword = jobspec['vncpassword'] if 'vncpassword' in jobspec else ''
    user = jobspec['username'] if 'username' in jobspec else None
    domain = jobspec['domain'] if 'domain' in jobspec else None
    password = jobspec['password'] if 'password' in jobspec else None
    print('password: %s'%password)
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
        otherjobspec['onlyfound'] = 'true'
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
                hostkeylists = split(hostkeys, n)
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
        elif typ == 'webscreenshot':
            # Fetch results for target subnet, only screenshot those with open ports
            port = jobspec['port'] if 'port' in jobspec else '80'
            scheme = jobspec['scheme'] if 'scheme' in jobspec else 'http'
            if port == '443':
                scheme = 'https'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly: # better have this set, or hardcode
                hosts = filter_by_port(hosts, port)
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            n = 30
            listlist = split(hostkeys, n)
            jobids = []
            for l in listlist:
                job = WebScreenshot(l, scheme, port)
                forkjob(job, scraperqueue)
                jobids.append(job.ident)
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
            n = 30
            listlist = split(hostkeys, n)
            jobids = []
            for l in listlist:
                job = RdpScreenshot(l, domain=domain, user=user, password=password)
                forkjob(job, scraperqueue)
                jobids.append(job.ident)
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
            n = 30
            listlist = split(hostkeys, n)
            jobids = []
            for l in listlist:
                job = VncScreenshot(l, port=port, password=vncpassword)
                forkjob(job, scraperqueue)
                jobids.append(job.ident)
        elif typ == 'smbenum':
            # Fetch results for target subnet, only screenshot those with open ports
            r = Results()
            r.read_all('results')
            dchost = jobspec['dchost'] if 'dchost' in jobspec else None
            print("DCHOST %s"%dchost)
            hosts = r.hosts
            hostkeys = []
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                hosts = filter_by_port(hosts, '445') # should this be 139 or 445?
            else:
                log('smbenum should target found only hosts')
                continue
            print('filtered: %s'%str(hosts.keys()))
            hostkeys = list(hosts.keys())
            if mask == '32':
                hostkeys = [target]
            n = 30
            listlist = split(hostkeys, n)
            log('listlist: %s'%str(listlist))
            log('hostkeys: %s'%str(hostkeys))
            jobids = []
            for l in listlist:
                enumjob = SmbEnum(l, domain=domain, user=user, password=password, dchost=dchost)
                forkjob(enumjob, scraperqueue)
                jobids.append(enumjob.ident)
                nmapjob = Nmap(l, script='smb*vuln*')
                forkjob(nmapjob, nmapqueue)
                jobids.append(nmapjob.ident)
        elif typ == 'snmpwalk':
            # Fetch results for target subnet, only screenshot those with open ports
            prefix = jobspec['prefix'] if 'prefix' in jobspec else None
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            hosts = filter_by_port(hosts, '161')
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
        elif typ == 'wappalyzer':
            # Fetch results for target subnet, only screenshot those with open ports
            port = jobspec['port'] if 'port' in jobspec else '80'
            scheme = ''
            if port == '443':
                scheme = 'https'
            else:
                scheme = 'http'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                sys.stderr.write('0: %s\n'%str(list(hosts.keys())))
                hosts = filter_by_port(hosts, port)
                sys.stderr.write('1: %s\n'%str(list(hosts.keys())))
            hostkeys = list(hosts.keys())
            job = Wappalyzer(hostkeys, port=port, scheme=scheme)
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
        elif typ == 'ms12_020':
            # Fetch results for target subnet, only screenshot those with open ports
            port = '3389'
            r = Results()
            r.read_all('results')
            hosts = r.hosts
            hosts = filter_by_network(hosts, target, mask)
            if foundonly:
                sys.stderr.write('0: %s\n'%str(list(hosts.keys())))
                hosts = filter_by_port(hosts, port)
                sys.stderr.write('1: %s\n'%str(list(hosts.keys())))
            hostkeys = list(hosts.keys())
            job = Ms12_020(hostkeys)
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

        
def make_app():
    return tornado.web.Application([
        (r"/jobs/(.*)", JobsHandler),
        (r"/api/jobs/(.*)", JobsHandler), # /api for the vue dev server api router
        (r"/api/results/(.*)", ResultsHandler), # ditto
        # route /ui to the vue app built with 'npm run build', no need to copy it
        (r"/ui/(.*)", tornado.web.StaticFileHandler, {"path": "ui/asscan/dist/",\
                                                      "default_filename": 'index.html'}),
        (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": "ui/asscan/dist/js/"}),
        (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": "ui/asscan/dist/css/"}),
        (r"/results/(.*)", ResultsHandler),
        (r"/notes/(.*)", NotesHandler),
        (r"/api/notes/(.*)", NotesHandler),
        (r"/scans/", ScansHandler),
        (r"/api/scans/", ScansHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "ui/asscan/dist/",\
                                                   "default_filename": 'index.html'}),
    ])

def main():
    app = make_app()
    if len(sys.argv) != 3:
        sys.stderr.write("usage: %s listen-port listen-host\n" % sys.argv[0])
        sys.stderr.write("If you run on anything else than inside a docker container,\n")
        sys.stderr.write("listen-host should be 127.0.0.1 unless you know what you are doing\n")
        sys.exit(0)
    app.listen(int(sys.argv[1]), sys.argv[2])
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
