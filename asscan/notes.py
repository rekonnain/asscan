# -*- coding: utf-8 -*-

import sys,json

filename='notes.json'


def notesforhost(hostname):
    j = {}
    try:
        j = json.loads(open(filename,'r').read())
    except:
        pass
    if hostname in j:
        return {hostname: j[hostname]}
    else:
        return {}


def savenote(host, note):
    j = {}
    try:
        j = json.loads(open(filename,'r').read())
    except:
        pass
    j[host] = note
    open(filename,'w').write(json.dumps(j, sort_keys = True, indent = 4))


def deletenote(host):
    j = {}
    try:
        j = json.loads(open(filename,'r').read())
        del j[host]
        open(filename,'w').write(json.dumps(j, sort_keys = True, indent = 4))
    except:
        pass
    

def hostswithcomments():
    try:
        j = json.loads(open(filename,'r').read())
        return j.keys()
    except:
        return []
    
