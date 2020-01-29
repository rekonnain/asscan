#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import jobdispatch as jd
import time
import socket

presence_channel = 'asscan/presence'
jobs_channel = 'asscan/job'

server_addr = 'mqtt1.local.lan'
identity = 'foo-1'

"""
This module implements a MQTT based infrastructure. An ASSCAN instance
can act either as a "server" or an "agent". Server can dispatch job (scan)
requests, and agents receive said requests and perform scans.

The supported MQTT messages are:
# Agent announces it's online on topic asscan/presence
{ "type": "announce-presence",
  "clientid": "192.168.9.20",
  "timestamp" : 1580305710.07 }

# Jobs
Server posts job spec on asscan/job
{ "type": "start-job-request",
  "target_nodes": [ 'foo-1', 'foo-2' ],
  "requestid": "[uuid]",
  "network": "192.168.9.0",
  "netmask": "24",
  "scantypes": [ "nmap", "rdpscreenshot" ] }

Agent responds
{ "type": "start-job-response",
  "requestid": "[uuid]",
  "jobid": "[another uuid]" }

Note that the agent and server classes depend on an external runloop,
which is fine, as tornado provides for that. The main application in server.py
is supposed to call the mqtt client instance's tick() method regularly.
Therefore, all periodic tasks can be implemented inside the tick() method.

"""



def agent_on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(jobs_channel)

def server_on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(presence_channel)

    
class agent:
    def on_message(self, client, userdata, msg):
        p = msg.payload.decode('utf-8')
        print(msg.topic + ": " + p)
        j = json.loads(msg.payload)
        mtype = j['type']
        if mtype == 'presence-request':
            print("reporting presence")
            response = { 'type': 'presence-response',
                         'clientid': identity }
            client.publish(presence_channel, json.dumps(response))
        elif mtype == 'start-job-request':
            self.startjob(j)

    def startjob(self, jobdesc):
        jd.forkjobs(jobdesc)
            
    def __init__(self, clientid):
        self.client = mqtt.Client()
        self.client.on_connect = agent_on_connect
        self.client.on_message = lambda c, u, m: self.on_message(c, u, m)
        self.last_presence_at = 0.0 # when did we last announce we are online
        self.ip = socket.gethostbyname(socket.gethostname()) # TODO maybe user configurable
        self.clientid = clientid

    def connect(self):
        print("Connecting")
        #print(self.client.on_connect)
        self.client.connect(server_addr, 1883, 60)
        #self.client.loop_forever()

    def tick(self):
        if time.time() - self.last_presence_at > 5.0:
            payload = { 'time': time.time(),
                        'clientid': self.clientid,
                        'ip': self.ip,
                        'type': 'announce-presence' }
            self.client.publish(presence_channel, json.dumps(payload))
            self.last_presence_at = time.time()
        self.client.loop(timeout=1.0)
        #pass

class server:
    def on_message(self, client, userdata, msg):
        p = msg.payload.decode('utf-8')
        j = json.loads(msg.payload)
        #print(json.dumps(j, sort_keys = True, indent = 4))
        if j['type'] == 'announce-presence':
            clientid = j['clientid']
            timestamp = j['time']
            ip = j['ip']
            #print(timestamp)
            if not clientid in self.connected_clients:
                print("New agent: %s"%clientid)
            self.connected_clients[clientid] = {'timestamp': timestamp,
                                                'ip': ip,
                                                'clientid': clientid}
            
    def prune_clients(self):
        for key in list(self.connected_clients.keys())[:]:
            if time.time() - self.connected_clients[key]['timestamp'] > 10.0:
                print("Removing stale agent %s"%key)
                del self.connected_clients[key]

    def get_clients(self):
        clients = list(self.connected_clients.values())
        for c in clients:
            del(c['timestamp'])
        return {'clients': clients}
            
    def startjob(self, jobdesc):
        jobdesc['type'] = 'start-job-request'
        self.client.publish(jobs_channel, json.dumps(jobdesc))
            
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = server_on_connect
        self.client.on_message = lambda c, u, m: self.on_message(c, u, m)
        self.connected_clients = {}

    def connect(self):
        print("Connecting")
        #print(self.client.on_connect)
        self.client.connect(server_addr, 1883, 60)
        #self.client.loop_forever()

    def tick(self):
        self.prune_clients()
        self.client.loop(timeout=1.0)
        #pass
    

if __name__=='__main__':
    a = agent()
    a.connect()
    a.client.loop_forever()
