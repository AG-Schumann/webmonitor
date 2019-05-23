from pymongo import MongoClient
import os


_client = MongoClient(os.environ['dispatcher_uri'])
db = _client['xebra_daq']

message_codes = {
    'err_not_armed' : 'Can\'t start, DAQ isn\'t armed',
    'err_not_running' : 'Can\'t stop, DAQ isn\'t running',
    'err_not_idle' : 'Can\'t arm, DAQ isn\'t idle',
    'err_invalid_json' : 'Invalid JSON',
    'err_name_exists' : 'A config with that name already exists, you can\'t add a new one',
    'err_no_name_exists' : 'No config with that name exists, you can\'t update it',

    'msg_start' : 'DAQ starting',
    'msg_arm' : 'DAQ arming',
    'msg_stop' : 'DAQ stopping',
    'msg_led' : 'LED calibration starting',
    'msg_cfg_update' : 'Config updated',
    'msg_new_cfg' : 'New config saved',
    }

status_map = [
        'idle',
        'arming',
        'armed',
        'running',
        'error',
        'unknown',
        ]

def user(meta):
    return {'client_addr' : meta['REMOTE_ADDR'] if 'REMOTE_ADDR' in meta else 'web',
            'client_name' : meta['REMOTE_HOST'] if 'REMOTE_HOST' in meta else 'web',
            'client_user' : meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}

def base_context(msgcode=None):
    modes = db['options'].distinct('name', {'detector' : {'$ne' : 'include'}})
    if 'bkg' in modes:
        modes.remove('bkg')
        modes = ['bkg'] + modes
    if 'led' in modes:
        modes.remove('led')
    context = {}
    context['modes'] = modes
    if msgcode is not None:
        context.update({'message' : message_codes.get(msgcode, '?')})

    return context

def config_context(**kwargs):
    context = base_context(**kwargs)
    modes = db['options'].distinct('name')
    context['modes'] = modes

    return context

def runs_context(**kwargs):
    context = base_context(**kwargs)

    return context

def UpdateDaqspatcher(req, **kwargs):
    kwargs.update({'user': user(req.META)['client_user']})
    print('Updating with args:', kwargs)
    db['system_control'].update_one({'subsystem' : 'daqspatcher'}, {'$set' : kwargs})
    return

def CurrentStatus():
    for row in db['status'].find({}).sort([('_id',-1)]).limit(1):
        if time.time() - int(str(row['_id'])[:8],16) > 20:
            return 'offline'
        return status_map[int(row['status'])]
