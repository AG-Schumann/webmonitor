from django.http import JsonResponse, HttpResponseNotModified
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

import datetime

from . import base


def client(meta):
    return {'client_addr' : meta['REMOTE_ADDR'] if 'REMOTE_ADDR' in meta else 'web',
            'client_name' : meta['REMOTE_HOST'] if 'REMOTE_HOST' in meta else 'web',
            'client_user' : meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}

@require_POST
def startstop(request):
    name = request.POST['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    status = base.db.GetSensorSetting(name, 'status')
    user = client(request.META)
    if status == 'online':
        base.db.ProcessCommandStepOne('stop %s' % name, user=user)
    elif status == 'offline':
        base.db.ProcessCommandStepOne('start %s' % name, user=user)
    return HttpResponseNotModified()

@require_POST
def change_address(request):
    new_vals = request.POST
    name = new_vals['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    old_vals = base.db.GetSensorSetting(name, 'address')
    if old_vals is None:
        return HttpResponseNotModified()
    user = client(request.META)
    if 'ip' in old_vals:
        if new_vals['ip'] != old_vals['ip']:
            base.db.SetSensorSetting(name, 'address.ip', new_vals['ip'])
            base.db.LogUpdate(name=name,
                              key='address.ip',
                              value=new_vals['ip'],
                              **user)
        elif int(new_vals['port']) != old_vals['port']:
            base.db.SetSensorSetting(name, 'address.port', int(new_vals['port']))
            base.db.LogUpdate(name=name,
                              key='address.port',
                              value=int(new_vals['port']),
                              **user)
    if 'tty' in old_vals:
        if new_vals['tty'] != old_vals['tty']:
            base.db.SetSensorSetting(name, 'address.tty', new_vals['tty'])
            base.db.LogUpdate(name=name,
                              key='address.tty',
                              value=new_vals['tty'],
                              **user)
        elif new_vals['serialID'] != old_vals['serialID']:
            base.db.SetSensorSetting(name, 'address.serialID', new_vals['serialID'])
            base.db.LogUpdate(name=name,
                              key='address.serialID',
                              value=new_vals['serialID'],
                              **user)
        elif 'baud' in old_vals and int(new_vals['baud']) != old_vals['baud']:
            base.db.SetSensorSetting(name, 'address.baud', int(new_vals['baud']))
            base.db.LogUpdate(name=name,
                              key='address.baud',
                              value=int(new_vals['baud']),
                              **user)
    return HttpResponseNotModified()

@require_POST
def log_command(request):
    user = client(request.META)
    base.db.ProcessCommandStepOne(request.POST['command'], user=user)
    return HttpResponseNotModified()

@require_POST
def change_reading(request):
    new_vals = request.POST
    name = new_vals['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    reading_name = new_vals['reading_name']
    old_vals = base.db.GetReading(name, reading_name)
    if old_vals is None:
        return HttpResponseNotModified()
    user = client(request.META)
    for key,func in zip(['status', 'readout_interval', 'recurrence', 'runmode'],
                        [str, int, int, str]):
        new_val = func(new_vals[key])  # django doesn't typecast
        if old_vals[key] != new_vals:
            base.db.UpdateReading(name, reading_name, key, new_val)
            base.db.LogUpdate(name=name,
                              reading=reading_name,
                              key=key,
                              value=new_val,
                              **user)

    alarms = []
    for lvl in range(len(old_vals['alarms'])):
        alarms = [float(new_vals[f'al_{lvl}_0'])]+alarms+[float(new_vals[f'al_{lvl}_1'])]
    for i in range(len(alarms)-1):
        if alarms[i] >= alarms[i+1]:
            return redirect(f'/doberview/detail/01/')
    del alarms
    for lvl, alarms in enumerate(old_vals['alarms']):
        for i, al in enumerate(alarms):
            new_val = float(new_vals[f'al_{lvl}_{i}'])
            if al != new_val:
                base.db.UpdateReading(name, reading_name, f'alarms.{lvl}.{i}', new_val)
                base.db.LogUpdate(name=name,
                                  reading=reading_name,
                                  key=f'alarms.{lvl}.{i}',
                                  value=new_val,
                                  **user)

    for rm, cfg in old_vals['config'].items():
        new_val = int(new_vals[f'{rm}_level'])
        if cfg['level'] != new_val:
            base.db.UpdateReading(name, reading_name, f'config.{rm}.level', new_val)
            base.db.LogUpdate(name=name,
                              reading=reading_name,
                              key=f'config.{rm}.level',
                              value=new_val,
                              **user)

    return HttpResponseNotModified()

@require_POST
def change_contact_status(request):
    info = request.POST
    user = client(request.META)
    base.db.updateDatabase('settings','contacts',cuts={},updates={'$set' : {'status' : -1}})
    for key in ['primary', 'secondary1', 'secondary2']:
        name = info[key]
        if name != 'None':
            base.db.updateDatabase('settings','contacts',cuts={'name' : name},
                    updates = {'$set' : {'status' : 1}})
            base.db.LogUpdate(field='contacts', active=name, **user)
    return HttpResponseNotModified()

@require_POST
def add_new_contact(request):
    info = request.POST
    user = client(request.META)
    contact = {'name' : info['firstname'] + info['lastname'][0],
            'email' : info['email'],
            'sms' : info['sms'],
            'status' : -1,
            'first_name' : info['firstname'],
            'last_name' : info['lastname'],
            }
    base.db.insertIntoDatabase('settings','contacts',contact)
    base.db.LogUpdate(field='contacts', new=info['firstname'] + info['lastname'][0], **user)
    return HttpResponseNotModified()
