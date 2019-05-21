from django.shortcuts import redirect
from django.views.decorators.http import require_POST

import datetime
import json
from . import base


@require_POST
def start(request):
    if base.CurrentStatus() != 'armed':
        return redirect('main', msgcode='err_not_armed')
    try:
        duration = int(request.POST['duration'])*60
    except KeyError:
        duration = 180
    print('Starting with duration %i' % duration)
    base.UpdateDaqspatcher(request, duration=duration, goal='start')
    return redirect('main', msgcode='msg_start')

@require_POST
def stop(request):
    if base.CurrentStatus() != 'running':
        return redirect('main', msgcode='err_not_running')
    print('Stopping')
    base.UpdateDaqspatcher(request, goal='stop')
    return redirect('main', msgcode='msg_stop')

@require_POST
def arm(request):
    if base.CurrentStatus() != 'idle':
        return redirect('main', msgcode='err_not_idle')
    params = request.POST
    kwargs = {'mode' : params['mode'],
            'goal' : 'arm',
            }
    if 'config_override' in params and len(params['config_override']) > 1:
        print(params['config_override'])
        try:
            kwargs['config_override'] = json.loads(params['config_override'])
        except:
            return redirect('main', msgcode='err_invalid_json')
    else:
        kwargs['config_override'] = {}
    print('Arming for %s' % params['mode'])
    print(params['config_override'])
    base.UpdateDaqspatcher(request, **kwargs)
    return redirect('main', msgcode='msg_arm')

@require_POST
def led(request):
    print('LED')
    return redirect('main', msgcode='msg_led')

@require_POST
def new_cfg(request):
    vals = request.POST
    doc = {}
    if vals['name'] in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_name_exists')
    for key in ['name', 'description', 'user', 'detector']:
        doc[key] = vals[key]
    if 'include' in vals:
        doc['include'] = list(map(lambda s : s.strip(' '),
                                  vals['include'].strip('[]').split(',')))
        if len(doc['include']) == 1 and doc['include'][0] == '':
            del doc['include']
    try:
        doc.update(json.loads(vals['content']))
    except:
        return redirect('config', msgcode='err_invalid_json')
    base.db['options'].insert_one(doc)
    return redirect('config', msgcode='msg_new_cfg')

@require_POST
def update_cfg(request):
    vals = request.POST
    doc = {}
    if vals['name'] not in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_no_name_exists')
    for key in ['description', 'user', 'detector']:
        doc[key] = vals[key]
    if 'include' in vals:
        doc['include'] = list(map(lambda s : s.strip(' '),
                                  vals['include'].strip('[]').split(',')))
        if len(doc['include']) == 1 and doc['include'][0] == '':
            del doc['include']
    try:
        doc.update(json.loads(vals['content']))
    except:
        return redirect('config', msgcode='err_invalid_json')
    base.db['options'].update_one({'name' : vals['name']}, {'$set' : doc})
    return redirect('config', msgcode='msg_cfg_update')

