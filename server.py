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
re_uuid = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)

import jobdispatch as jd
import mqtt as m

class dummy:
    pass
state = dummy()
state.is_server = False

class ScansHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(jd.get_scans())

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
        filters = {}
        filters['prefix'] = self.get_query_argument('prefix', None)
        filters['port'] = self.get_query_argument('port', None)
        filters['service'] = self.get_query_argument('service', None)
        filters['vulns'] = self.get_query_argument('vulns', None)
        filters['screenshots'] = self.get_query_argument('screenshots', None)
        filters['notes'] = self.get_query_argument('notes', None)
        self.write(get_results(args, filters))
    
            
# information on current scan jobs
class JobsHandler(tornado.web.RequestHandler):
    def get(self, shit):
        args = shit.split('/')
        if args[0] == 'overview':
            self.write(jd.get_jobs_overview())
        elif args[0] == 'status':
            self.write(jd.get_jobs_status())
        else:
            self.write({'error': 'fuck off'})

    # submits a new scan job
    def post(self, dummy = None):
        jobspec = json_decode(self.request.body)
        print(json.dumps(jobspec, indent = 4, sort_keys = True))
        if state.is_server:
            print("I'm a server")
            state.mclient.startjob(jobspec)
        else:
            self.write(jd.forkjobs(jobspec))

class AgentsHandler(tornado.web.RequestHandler):
    def get(self):
        if state.is_server:
            self.write(state.mclient.get_clients())
        else:
            self.write({})
        
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
        (r"/agents/", AgentsHandler),
        (r"/api/agents/", AgentsHandler),
        (r"/scans/", ScansHandler),
        (r"/api/scans/", ScansHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "ui/asscan/dist/",\
                                                   "default_filename": 'index.html'}),
    ])

def main():
    serverport = 8888
    
    # mqtt
    if sys.argv[1] == 'agent':
        if len(sys.argv) == 3:
            state.mclient = m.agent(sys.argv[2])
            serverport = 8889
        else:
            print("usage: %s agent agent-id"%sys.argv[0])
            sys.exit(0)
    elif sys.argv[1] == 'server':
        state.mclient = m.server()
        state.is_server = True
    else:
        print('usage: %s [ server | client ]'%sys.argv[0])
        sys.exit(0)

    app = make_app()
    app.listen(serverport, address='127.0.0.1') # better not expose this
    c = tornado.ioloop.PeriodicCallback(lambda: state.mclient.tick(), callback_time = 1000.0)
    c.start()
    print("mqtt client running: " + str(c.is_running()))
    try:
        state.mclient.connect()
        tornado.ioloop.IOLoop.current().start()
    except:
        print("Stopping callback")
        c.stop()

if __name__ == "__main__":
    main()
