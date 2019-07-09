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
    base.UpdateDaqspatcher(request, duration=duration, goal='start',
            comment=request.POST['comment'])
    return redirect('main', msgcode='msg_start')

@require_POST
def stop(request):
    if base.CurrentStatus() not in ['armed','running']:
        return redirect('main', msgcode='err_not_running')
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
        try:
            kwargs['config_override'] = json.loads(params['config_override'])
        except:
            return redirect('main', msgcode='err_invalid_json')
    else:
        kwargs['config_override'] = {}
    base.UpdateDaqspatcher(request, **kwargs)
    return redirect('main', msgcode='msg_arm')

@require_POST
def led(request):
    base.UpdateDaqspatcher(request, goal='led')
    return redirect('main', msgcode='msg_led')

@require_POST
def cfg(request, act='update'):
    vals = request.POST
    doc = {}
    if act=='new' and vals['name'] in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_name_exists')
    if act=='update' and vals['name'] not in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_no_name_exists')

    for key in ['name', 'description', 'user', 'detector']:
        doc[key] = vals[key]
    if 'includes' in vals:
        doc['includes'] = list(map(lambda s : s.strip(' '),
                                  vals['includes'].split(',')))
        if len(doc['includes']) == 1 and doc['includes'][0] == '':
            del doc['includes']
    try:
        if 'content' in vals and len(vals['content']) > 2:
            doc.update(json.loads(vals['content']))
    except:
        return redirect('config', msgcode='err_invalid_json')
    base.db['options'].replace_one({'name' : vals['name']}, doc, upsert=True)
    msgcode = 'msg_new_cfg' if act=='new' else 'msg_cfg_update'
    return redirect('config', msgcode=msgcode)

