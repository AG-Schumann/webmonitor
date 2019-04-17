from django.http import HttpResponseRedirect, HttpResponseNotModified
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

import datetime
from . import base


@require_POST
def start(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'armed':
        return -1
    run_number = getNextRunNumber()
    start_time = datetime.datetime.now()
    run_id = start_time.strftime('%Y%m%d_%H%M')
    statusdoc = client['kodiaq']['status'].find_one()
    mode = statusdoc['mode']
    try:
        duration = int(request.POST['duration'])*60
    except KeyError:
        duration = 180
    command = base.base_command('start')
    command
    start_doc = {
            "command" : "start",
            "host" : "charon",
            "name" : run_name,
            "number" : run_number,
            "run_identifier" : run_id,
            "user" : user,
            "acknowledged" : [],
    }
    client['kodiaq']['commands'].insert_one(start_doc)
    return HttpResponseNotModified()

@require_POST
def stop(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    if getCurrentStatus() != 'running':
        return HttpResponseRedirect('/status',content={'message' : 'DAQ isn\'t running, can\'t stop'})
    user = base.user(request.META)
    coll.insert_one({'command' : 'stop', 'logged' : datetime.datetime.now(), 'user' : user})
    client.close()
    return HttpResponseNotModified()

@require_POST
def arm(request):
    params = request.POST
    if 'config_override' in params:
        print(params['config_override'])
    if 'registers' in params:
        print(params['registers'])
    return HttpResponseNotModified()
