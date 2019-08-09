from django.http import JsonResponse

import datetime
from . import base
from pymongo.son_manipulator import ObjectId


def get_runs(request, experiment="xebra", limit=None):
    runs = []
    query = {'experiment' : experiment}
    projection = 'run_id tags mode start end duration user comment'.split()
    cursor = base.db['runs'].find(query, projection).sort([('run_id', -1)])
    if limit is not None:
        cursor.limit(int(limit))
    for row in cursor:
        if 'end' in row:
            end = row['end'].strftime('%Y-%m-%d %H:%M')
            duration = (row['end']-row['start']).total_seconds()
        else:
            end = 'active'
            duration = (datetime.datetime.utcnow() - row['start']).total_seconds()
        doc = {
                'run_id' : '%i' % row['run_id'],
                'tags' : row['tags'],
                'mode' : row['mode'],
                'start' : row['start'].strftime('%Y-%m-%d %H:%M'),
                'end' : end,
                'duration' : '%i' % duration,
                'user' : row['user'],
                'meshes' : ('%d/%d' % (doc['cathode_mean'], doc['anode_mean'])
                    if 'anode_mean' in doc else '-/-')
                'comment' : row['comment'] if 'comment' in row else '',
        }
        runs.append(doc)
    return JsonResponse({'runs' : runs})

def get_status_history(request):
    rows = []
    for row in base.db['status'].find({}).sort([('_id', -1)]).limit(5):
        rows.append({
            'time' : row['_id'].generation_time.strftime('%H:%M:%S'),
            'rate' : f"{row['rate']:.3g}",
            'status' : base.status_map[row['status']],
            'run_id' : row['current_run_id'],
            'run_mode' : row['run_mode'],
        })
    return JsonResponse({'rows' : rows})

def get_status(request):
    ret = {}
    #status_doc = base.db['system_control'].find_one({'subsystem' : 'daq'})
    #ret['daqstatus'] = status_doc['status']
    #ret['daqmsg'] = status_doc['msg'] if status_doc['msg'] else ''
    ret['daqstatus'] = base.CurrentStatus()
    ret['daqmsg'] = ''
    for doc in base.db['log'].find({}).sort([('_id', -1)]).limit(1):
        ret['daqmsg'] = doc['message']

    status_doc = base.db['system_control'].find_one({'subsystem' : 'daqspatcher'})
    ret['spatchstatus'] = status_doc['status']
    ret['spatchmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    status_doc = base.db['system_control'].find_one({'subsystem' : 'straxinator'})
    ret['straxstatus'] = status_doc['status']
    ret['straxmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    status_doc = base.db['system_control'].find_one({'subsystem' : 'pulser'})
    ret['ledstatus'] = status_doc['status']
    #ret['ledmsg'] = status_doc['msg'] if status_doc['msg'] else ''
    return JsonResponse(ret)

def get_cfg_doc(request, name):
    doc = base.db['options'].find_one({'name' : name})
    if doc is None:
        return JsonResponse({'name' : '', 'description' : '', 'user' : '', 'detector' : ''})
    del doc['_id']
    return JsonResponse(doc)

def get_run_detail(request, experiment, runid):
    runid = f'{int(runid):05d}'
    doc = base.db['runs'].find_one({'experiment' : experiment, 'run_id' : runid})
    if doc is None:
        return JsonResponse({})
    del doc['_id']
    if 'end' in doc:
        doc['duration'] = (doc['end']-doc['start']).total_seconds()
        doc['end'] = doc['end'].isoformat(sep=' ')
    else:
        doc['duration'] = 'Active'
        doc['end'] = 'None'
    doc['start'] = doc['start'].isoformat(sep=' ')
    return JsonResponse(doc)
