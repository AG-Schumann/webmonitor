from django.shortcuts import redirect
from django.http import HttpResponseNotModified
from django.views.decorators.http import require_POST

import datetime
import json
from . import base
import time


@require_POST
def start(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    params = request.POST

    base.db['djangostatus'].insert({"params": params})

    kwargs = {'mode': params['mode'],
              'goal': 'arm',
              }
    if 'config_override' in params and len(params['config_override']) > 1:
        try:
            kwargs['config_override'] = json.loads(params['config_override'])
        except:
            return redirect('main', msgcode='err_invalid_json')
    else:
        kwargs['config_override'] = {}

    if ("button" not in params) or (params["button"] == "Start"):
        if base.current_status() != 'idle':
            return redirect('main', msgcode='err_not_idle')

        base.db['djangostatus'].insert({"COMMAND_Start": 1})
        base.update_daqspatcher(request, **kwargs)
        #  base.db['djangostatus'].insert({"status":"start sleep(5)"})
        #  time.sleep(5)  # one sec for dispatcher, one for daq, one extra
        for _ in range(15):
            status = base.current_status()

            if status not in ['arming', 'armed', "idle"]:
                return redirect('main', msgcode='err_not_arming')
            if status == 'armed':
                break
            time.sleep(1)

        if status != 'armed':
            base.db['djangostatus'].insert({"status": "not armed"})
            return redirect('main', msgcode='err_not_armed')
        try:
            duration = int(request.POST['duration']) * 60
        except KeyError:
            duration = 180

        base.update_daqspatcher(request, duration=duration, goal='start',
                                comment=request.POST['comment'])
        return redirect('main', msgcode='msg_start')

    elif params["button"] == "Append":
        base.db['djangostatus'].insert({"COMMAND_Append": 1})

        list_params_tosave = ["duration", "mode", "comment", "config_override"]
        params_tosave = {key: params[key] for key in list_params_tosave}
        params_tosave["experiment"] = "xebra"

        base.db['djangostatus'].insert(params_tosave)
        base.db['runs_todo'].insert(params_tosave)
        return redirect('main', msgcode='msg_start')
    else:
        return redirect('main', msgcode='msg_start')


@require_POST
def stop(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    if base.current_status() not in ['armed', 'running']:
        return redirect('main', msgcode='err_not_running')
    base.update_daqspatcher(request, goal='stop')
    return redirect('main', msgcode='msg_stop')


@require_POST
def pause_toggle(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    current_status = base.db['system_control'].find_one({'subsystem': 'daqspatcher'})["worklist"]

    if current_status == "running":
        new_state = "paused"
    else:
        new_state = "running"

    base.update_daqspatcher(request, worklist=new_state)
    return redirect('main')


@require_POST
def led(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    base.update_daqspatcher(request, goal='led')
    base.update_daqspatcher(request, run_duration='180')
    return redirect('main', msgcode='msg_led')


@require_POST
def cfg(request, act='update'):
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    vals = request.POST
    doc = {}
    if act == 'new' and vals['name'] in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_name_exists')
    if act == 'update' and vals['name'] not in base.db['options'].distinct('name'):
        return redirect('config', msgcode='err_no_name_exists')

    for key in ['name', 'description', 'user', 'detector']:
        doc[key] = vals[key]
    if 'includes' in vals:
        doc['includes'] = list(map(lambda s: s.strip(' '),
                                   vals['includes'].split(',')))
        if len(doc['includes']) == 1 and doc['includes'][0] == '':
            del doc['includes']
    try:
        if 'content' in vals and len(vals['content']) > 2:
            doc.update(json.loads(vals['content']))
    except:
        return redirect('config', msgcode='err_invalid_json')
    base.db['options'].replace_one({'name': vals['name']}, doc, upsert=True)
    msgcode = 'msg_new_cfg' if act == 'new' else 'msg_cfg_update'
    return redirect('config', msgcode=msgcode)


@require_POST
def update_run(request):
    print('Updating run')
    if not base.is_schumann_subnet(request.META):
        return redirect('main', msgcode='err_not_auth')
    vals = request.POST
    try:
        experiment, run_id = vals['exp_name'].split('__')
    except ValueError:
        return redirect('runs')
    query = {'experiment': experiment, 'run_id': int(run_id)}
    doc = base.db['runs'].find_one(query, projection={'tags': 1, 'comment': 1})
    existing_tags = doc['tags']
    existing_comment = doc['comment']

    if 'newtag' in vals and len(vals['newtag']) > 1 and vals['newtag'] not in existing_tags:
        base.db['runs'].update_one(query, {'$push': {'tags': vals['newtag']}})
    tags_to_remove = []
    for key in vals:
        if key.startswith('rm_'):
            tags_to_remove.append(key.split('rm_')[1])
    if len(tags_to_remove) > 0:
        base.db['runs'].update_one(query, {'$pull': {'tags': {'$in': tags_to_remove}}})
    if existing_comment != vals['run_comment']:
        base.db['runs'].update_one(query, {'$set': {'comment': vals['run_comment']}})
    return redirect('/control/runs')
