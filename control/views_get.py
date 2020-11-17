from django.http import JsonResponse

import datetime
from . import base
from pymongo.son_manipulator import ObjectId


def get_runs(request, experiment="xebra", limit=None):
    runs = []
    query = {'experiment': experiment}
    projection = 'run_id tags mode start end duration user comment'.split()
    cursor = base.db['runs'].find(query, projection).sort([('run_id', -1)])
    if limit is not None:
        cursor.limit(int(limit))
    for row in cursor:
        if 'end' in row:
            end = row['end'].strftime('%Y-%m-%d %H:%M')
            duration = (row['end'] - row['start']).total_seconds()
        else:
            end = 'active'
            duration = (datetime.datetime.utcnow() - row['start']).total_seconds()
        doc = {
            'run_id': '%i' % row['run_id'],
            'mode': row['mode'],
            'start': row['start'].strftime('%Y-%m-%d %H:%M'),
            'end': end,
            'duration': '%i' % duration,
            'user': row['user'],
            'meshes': ('%d/%d' % (row['cathode_mean'], row['anode_mean'])
                       if 'anode_mean' in row else '-/-'),
            'comment': row['comment'] if 'comment' in row else '',
        }
        runs.append(doc)
    return JsonResponse({'runs': runs})


def get_status_history(request):
    rows = []
    for row in base.db['status'].find({}).sort([('_id', -1)]).limit(5):
        rows.append({
            'time': row['_id'].generation_time.strftime('%H:%M:%S'),
            'rate': f"{row['rate']:.3g}",
            'status': base.status_map[row['status']],
            'run_id': row['current_run_id'],
            'run_mode': row['run_mode'],
        })
    return JsonResponse({'rows': rows})


def get_status(request):
    ret = {'daqstatus': base.current_status(), 'daqmsg': ''}
    # status_doc = base.db['system_control'].find_one({'subsystem' : 'daq'})
    # ret['daqstatus'] = status_doc['status']
    # ret['daqmsg'] = status_doc['msg'] if status_doc['msg'] else ''
    for doc in base.db['log'].find({}).sort([('_id', -1)]).limit(1):
        ret['daqmsg'] = doc['message']

    status_doc = base.db['system_control'].find_one({'subsystem': 'daqspatcher'})
    ret['spatchstatus'] = status_doc['status']
    ret['daqworklist'] = status_doc['worklist']
    ret['spatchmsg'] = status_doc['msg'] if status_doc['msg'] else ''
    if ret['daqstatus'] == 'running':
        run_duration = status_doc['duration']
        # run_start = base.db['runs'].find_one({},{'start': 1}).sort([('_id', -1)])['start']
        run_start = \
            list(base.db["runs"].aggregate(
                [{'$match': {"start": {'$exists': 1}}}, {'$sort': {"_id": -1}}, {'$limit': 1}]))[
                0]["start"]
        runtime = (datetime.datetime.utcnow() - run_start).total_seconds()
        ret['runprogress'] = runtime
        ret['run_duration'] = run_duration
    else:
        ret['runprogress'] = '0'
        ret['run_duration'] = '1'

    status_doc = base.db['system_control'].find_one({'subsystem': 'straxinator'})
    ret['straxstatus'] = status_doc['status']
    ret['straxmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    status_doc = base.db['system_control'].find_one({'subsystem': 'pulser'})
    ret['ledstatus'] = status_doc['status']
    # ret['ledmsg'] = status_doc['msg'] if status_doc['msg'] else ''

    return JsonResponse(ret)


def get_cfg_doc(request, name):
    doc = base.db['options'].find_one({'name': name})
    if doc is None:
        return JsonResponse({'name': '', 'description': '', 'user': '', 'detector': ''})
    del doc['_id']
    return JsonResponse(doc)


def get_run_detail(request, experiment, runid):
    doc = base.db['runs'].find_one({'experiment': experiment, 'run_id': int(runid)})
    if doc is None:
        return JsonResponse({})
    del doc['_id']
    if 'end' in doc:
        doc['duration'] = (doc['end'] - doc['start']).total_seconds()
        doc['end'] = doc['end'].isoformat(sep=' ')
    else:
        doc['duration'] = 'Active'
        doc['end'] = 'None'
    doc['start'] = doc['start'].isoformat(sep=' ')


def get_upcoming_runs(request, experiment):
    int_runs = base.db["runs_todo"].count_documents({'experiment': experiment})

    int_duration = sum([int(x["duration"]) for x in
                        list(base.db["runs_todo"].find({'experiment': experiment, "duration": {'$exists': 1}}))])
    int_duration += base.db["runs_todo"].count_documents({"duration": {'experiment': experiment, '$exists': 0}}) * 3

    return JsonResponse({"runs": int_runs, "duration": int_duration})


def get_upcoming_runs_list(request, experiment):
    docs = base.db["runs_todo"].find({'experiment': experiment})
    runs = []
    for this_doc in docs:
        this_run = {
            "id": str(this_doc["_id"]),
            "mode": this_doc["mode"],
            "comment": this_doc["comment"],
            "duration": this_doc["duration"],
            "config_override": this_doc["config_override"],
        }

        runs.append(this_run)

    return JsonResponse({"runs": runs})


def clear_upcoming_runs(request, experiment):
    if not base.is_schumann_subnet(request.META):
        return JsonResponse({"OK": False, "msg": "user is not authorized"})

    base.db["runs_todo"].delete_many({'experiment': experiment})
    return JsonResponse({
        "OK": True,
        "experiment": experiment
    })


def clear_a_upcoming_run(request, experiment, objectid):
    if not base.is_schumann_subnet(request.META):
        return JsonResponse({"OK": False, "msg": "user is not authorized"})

    base.db["runs_todo"].delete_many({'experiment': experiment, '_id': ObjectId(objectid)})

    return JsonResponse({
        "OK": True,
        "experiment": experiment,
        "objectid": objectid,
    })
