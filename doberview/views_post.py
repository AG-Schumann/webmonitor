from django.http import JsonResponse, HttpResponseNotModified
from django.views.decorators.http import require_POST
from django.shortcuts import redirect

import datetime
import time

from . import base


def client(meta):
    return {'client_addr' : meta['REMOTE_ADDR'],
            'client_name' : meta['REMOTE_HOST'],
            'client_user' : meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}

@require_POST
def startstop(request, name=""):
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    status = base.db.GetSensorSettings(name)['status']
    user = client(request.META)
    print(user)
    if status == 'online':
        print('Online, stopping ', name)
        #base.db.ParseCommand('stop %s' % name, user=user)
    elif status == 'offline':
        print('Offline, starting ', name)
        #base.db.ParseCommand('start %s' % name, user=user)
    time.sleep(5)
    print()
    return HttpResponseNotModified()

@require_POST
def change_address(request, name=""):
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    old_vals = base.db.GetSensorSetting(name, 'address')
    new_vals = request.POST
    user = client(request.META)
    print(user)
    if 'ip' in old_vals:
        if new_vals['ip'] != old_vals['ip']:
            print('ip: ', new_vals['ip'])
            #base.db.SetSensorSetting(name, 'address.ip', new_vals['ip'])
            #base.db.LogUpdate(f'{name}.address.ip', new_vals['ip'], user)
        elif new_vals['port'] != old_vals['port']:
            print('port: ', new_vals['port'])
            #base.db.SetSensorSetting(name, 'address.port', int(new_vals['port']))
            #base.db.LogUpdate(f'{name}.address.port', int(new_vals['port']), user)
    elif 'tty' in old_vals:
        if new_vals['tty'] != old_vals['tty']:
            print('tty: ', new_vals['tty'])
            #base.db.SetSensorSetting(name, 'address.tty', new_vals['tty'])
            #base.db.LogUpdate(f'{name}.address.tty', new_vals['tty'], user)
        elif new_vals['serialID'] != old_vals['serialID']:
            print('serialID: ', new_vals['serialID'])
            #base.db.SetSensorSetting(name, 'address.serialID', new_vals['serialID'])
            #base.db.LogUpdate(f'{name}.address.serialID', new_vals['serialID'], user)
    print()
    return HttpResponseNotModified()

@require_POST
def log_command(request):
    user = client(request.META)
    print(user)
    print('Command: ', request.POST['command'])
    print()
    #base.db.ParseCommand(request.POST['command'], user=user)
    return HttpResponseNotModified()

@require_POST
def change_reading(request, name=""):
    if name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    new_vals = request.POST
    reading_name = new_vals['reading_name']
    old_vals = base.db.GetReading(name, reading_name)
    user = client(request.META)
    print(user)
    if old_vals['readout_interval'] != new_vals['readout_interval']:
        print('Readout interval: ', new_vals['readout_interval'])
        #base.db.UpdateReading(name, reading_name, 'readout_interval', new_vals['readout_interval'])
        #base.db.LogUpdate(f'{name}-{reading_name}.readout_interval', new_vals['readout_interval'],
        #        user)
    if old_vals['recurrence'] != new_vals['alarm_rec']:
        print('Recurrence: ', new_vals['alarm_rec'])
        #base.db.UpdateReading(name, reading_name, 'recurrence', new_vals['alarm_red'])
        #base.db.LogUpdate(f'{name}-{reading_name}.recurrence', new_vals['alarm_rec'], user)
    if old_vals['runmode'] != new_vals['runmode']:
        print('Runmode: ', new_vals['runmode'])
        #base.db.UpdateReading(name, reading_name, 'runmode', new_vals['runmode'])
        #base.db.LogUpdate(f'{name}.runmode', new_vals['runmode'], user)
    alarms = []
    for lvl in range(len(old_vals['alarms'])):
        alarms = [float(new_vals[f'al_{lvl}_0'])] + alarms + [float(new_vals[f'al_{lvl}_1'])]
    for i in range(len(alarms)-1):
        if alarms[i] >= alarms[i+1]:
            print(f'Alarm {i}-{i+1} invalid')
            return redirect(f'/doberview/detail/{name}/01/')
    print(alarms)
    del alarms
    for lvl, alarms in enumerate(old_vals['alarms']):
        for i, al in enumerate(alarms):
            if al != new_vals[f'al_{lvl}_{i}']:
                print(f'Alarm {lvl} {i} ', new_vals[f'al_{lvl}_{i}'])
                #base.db.UpdateReading(name, reading_name, f'alarms.{lvl}.{i}',
                #        new_vals[f'al_{lvl}_{i}'])
                #base.db.LogUpdate(f'{name}-{reading_name}.alarms.{lvl}.{i}',
                #        new_vals[f'al_{lvl}_{i}'], user)
    print()
    return HttpResponseNotModified()
