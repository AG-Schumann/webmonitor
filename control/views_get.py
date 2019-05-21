from django.http import JsonResponse

import datetime
from . import base
from pymongo.son_manipulator import ObjectId


def get_runs(request, limit=5):
    runs = []
    for row in base.db['runs'].find({},{'config' : 0}).sort([('number', -1)]).limit(5):
        if 'end' in row:
            end = row['end'].strftime('%Y-%m-%d %H:%M')
            duration = (row['end']-row['start']).total_seconds()
        else:
            end = 'active'
            duration = (datetime.datetime.now() - row['start']).total_seconds()

        doc = {
                'run_id' : '%i' % row['run_id'],
                'mode' : row['mode'],
                'start' : row['start'].strftime('%Y-%m-%d %H:%M'),
                'end' : end,
                'duration' : '%i' % duration,
                'user' : row['user'],
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
    status_doc = base.db['system_control'].find_one({'subsystem' : 'daq'})
    ret['daqstatus'] = status_doc['status']
    ret['daqmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    status_doc = base.db['system_control'].find_one({'subsystem' : 'daqspatcher'})
    ret['spatchstatus'] = status_doc['status']
    ret['spatchmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    status_doc = base.db['system_control'].find_one({'subsystem' : 'straxinator'})
    ret['straxstatus'] = status_doc['status']
    ret['straxmsg'] = status_doc['msg'] if status_doc['msg'] else ''
    return JsonResponse(ret)

def get_cfg_doc(request, name):
    doc = base.db['options'].find_one({'name' : name})
    if doc is None:
        return JsonResponse({'name' : '', 'description' : '', 'user' : '', 'detector' : ''})
    del doc['_id']
    return JsonResponse(doc)
