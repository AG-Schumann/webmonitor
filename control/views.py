from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from pymongo import MongoClient
import time
import datetime
import os

def getNextRunNumber():
    client = MongoClient(os.environ['MONITOR_URI'])
    coll = client['runs']['xebra']
    last_run_number = -1
    for row in coll.find({'tc' : 1},{'number' : 1}).sort([('start', -1)]).limit(1):
        last_run_number = int(row['number'])
    client.close()
    return last_run_number + 1

def getCurrentStatus():
    client = MongoClient(os.environ['MONITOR_URI'])
    doc = client['kodiaq']['status'].find_one()
    client.close()
    if 'strax' in doc['status']:
        return 'straxinating'
    return doc['status']

def status(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    modes = client['kodiaq']['config'].distinct('mode')
    client.close()
    if 'bkg' in modes:  # so 'bkg' is first in the list
        modes.remove('bkg')
        modes = ['bkg'] + modes
    ret = {'modes' : modes, 'message' : ''}
    ret.update(get_runs())
    return render(request, 'control/index.html', ret)

def get_runs(limit=5):
    client = MongoClient(os.environ['MONITOR_URI'])
    runs_coll = client['runs']['xebra']
    runs = []
    for row in runs_coll.find({'tc' : 0},{'name' : 1, 'number' : 1, 'mode' : 1, 'start' : 1, 'end' : 1, 'duration' : 1, '_id' : 0}).sort([('start', -1)]).limit(5):
        if 'end' in row:
            end = row['end'].strftime('%Y-%m-%d %H:%M')
            duration = (row['end']-row['start']).total_seconds()
        else:
            end = 'active'
            duration = (datetime.datetime.now() - row['start']).total_seconds()

        doc = {
                'number' : '%i' % row['number'],
                'name' : row['name'],
                'mode' : row['mode'],
                'start' : row['start'].strftime('%Y-%m-%d %H:%M'),
                'end' : end,
                'duration' : '%i' % duration
        }
        runs.append(doc)
    client.close()
    return {'runs' : runs}

def get_status(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    doc = client['kodiaq']['status'].find_one()
    del doc['_id']
    for k in ['mode','name','number']:
        if k not in doc:
            doc[k] = 'none'
    return JsonResponse(doc)

def get_status_history(request, limit=5):
    client = MongoClient(os.environ['MONITOR_URI'])
    coll = client['kodiaq']['history']
    ret = {'time' : [], 'rate' : [], 'freq' : []}
    for row in coll.find({}).sort([('time', -1)]).limit(5):
        ret['time'].append(datetime.datetime.fromtimestamp(row['time']).strftime('%H:%M:%S'))
        ret['rate'].append('%.3g' % row['rate'])
        ret['freq'].append('%.3g' % row['freq'])
    client.close()
    return JsonResponse(ret)

def start(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'armed':
        return HttpResponseRedirect('/status',content={'message' : 'DAQ isn\'t armed, can\'t start'})
    run_number = getNextRunNumber()
    start_time = datetime.datetime.now()
    run_name = start_time.strftime('%Y%m%d_%H%M')
    statusdoc = client['kodiaq']['status'].find_one()
    mode = statusdoc['mode']
    try:
        duration = int(request.POST['duration'])*60
    except KeyError:
        duration = 180
    start_doc = {
            "command" : "start",
            "name" : run_name,
            "number" : run_number,
            "logged" : time.time()
    }
    client['kodiaq']['commands'].insert_one(start_doc)
    rundoc = {
            "name" : run_name,
            "number" : run_number,
            "start" : start_time,
            "mode" : mode,
            "ini" : client['kodiaq']['config'].find_one({'mode' : mode}),
            "user" : "web",
            "tc" : 1
    }
    client['runs']['xebra'].insert_one(rundoc)
    stop_doc = {
            "command" : "stop",
            "logged" : time.time() + duration
    }
    client['kodiaq']['commands'].insert_one(stop_doc)
    client.close()
    return HttpResponseRedirect('/control')

def stop(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'running':
        return HttpResponseRedirect('/status',content={'message' : 'DAQ isn\'t running, can\'t stop'})
    to_delete = {
            "command" : "stop",
            "logged" : {"$gte" : time.time()}
    }
    client['kodiaq']['commands'].delete_many(to_delete)
    stop_doc = {
            "command" : "stop",
            "logged" : time.time()
    }
    client['kodiaq']['commands'].insert_one(stop_doc)
    client.close()
    return HttpResponseRedirect('/control')

def arm(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'idle':
        return HttpResponseRedirect('/status',content={'message' : 'DAQ isn\'t idle, can\'t arm'})
    mode = request.POST['mode']
    arm_doc = {
            "command" : "arm",
            "mode" : mode,
            "logged" : time.time()
    }
    client['kodiaq']['commands'].insert_one(arm_doc)
    client.close()
    return HttpResponseRedirect('/control')

def disarm(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'armed':
        return HttpResponseRedirect('/status',content={'message' : 'DAQ isn\'t arm, can\'t disarm'})
    disarm_doc = {
            "command" : "disarm",
            "logged" : time.time()
    }
    client['kodiaq']['commands'].insert_one(disarm_doc)
    client.close()
    return HttpResponseRedirect('/control')
