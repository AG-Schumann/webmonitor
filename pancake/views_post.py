from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from Doberman import dispatcher
import datetime
from math import isclose
from . import views_get
from . import base

@require_POST
def startstop(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    name = request.POST['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return redirect('/pancake/detail/')
    status = base.db.GetSensorSetting(name, 'status')
    user = base.client(request.META)
    if status == 'online':
        dispatcher.ProcessCommand(base.db, f'stop {name}', user=user)
    elif status == 'offline':
        dispatcher.ProcessCommand(base.db, f'start {name}' % name, user=user)
    return redirect('/pancake/detail/')

@require_POST
def change_address(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    new_vals = request.POST
    name = new_vals['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return redirect('/pancake/detail/')
    old_vals = base.db.GetSensorSetting(name, 'address')
    if old_vals is None:
        return redirect('/pancake/detail/')
    user = base.client(request.META)
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
    return redirect('/pancake/detail/')

@require_POST
def log_command(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    user = base.client(request.META)
    dispatcher.ProcessCommand(base.db,request.POST['command'], user=user)
    return redirect('/pancake/detail/')

@require_POST
def change_reading(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    new_vals = request.POST
    sensor = new_vals['sensor_name']
    if sensor not in base.db.Distinct('settings','sensors','name'):
        return redirect('/pancake/detail/')
    reading_name = new_vals['reading_name']
    old_vals = base.db.GetReadingSetting(sensor, reading_name)
    if old_vals is None:
        return redirect('/pancake/detail/')
    user = base.client(request.META)
    for key,func in zip(['status', 'readout_interval', 'runmode'],
                        [str, int, str]):
        new_val = func(new_vals[key])  # django doesn't typecast
        if old_vals[key] != new_vals:
            base.db.SetReadingSetting(sensor, reading_name, key, new_val)
            base.db.LogUpdate(name=sensor,
                              reading=reading_name,
                              key=key,
                              value=new_val,
                              **user)
    
    old_alarms = old_vals['alarms']
    new_alarms = []
    for old_alarm in old_alarms:
        al_type = old_alarm['type']
        max_duration = {}
        levels = {}
        new_alarm = {'type': al_type}
        for key in new_vals.keys():
            if key.startswith(al_type):
                parameter = key.split("__")[1]
                if parameter.startswith('al'):
                    #alarm levels for pid and simple
                    levels[parameter[3:]] = float(new_vals[key])
                elif parameter.startswith('max_duration'):
                    # alarm levels for time_since
                    levels[parameter[13:]] = float(new_vals[key])
                elif parameter == 'enabled':
                    new_alarm[parameter] = new_vals[key]
                else:
                    new_alarm[parameter] = float(new_vals[key])
        if len(levels) > 0:
            new_levels = []
            for i in range(len(levels)//2):
                new_levels.append([levels[f'{i}_0'], levels[f'{i}_1']])
            new_alarm['levels'] = new_levels
        if len(max_duration) > 0:
            new_max_d = []
            for i in range(len(max_duration)):
                new_max_d.append(max_duration[f'{i}'])
            new_alarm['max_duration'] = new_max_d
        if new_alarm != old_alarm:       
            base.db.UpdateAlarm(reading_name, new_alarm)

    for rm, cfg in old_vals['config'].items():
        new_val = int(new_vals[f'{rm}_level'])
        if cfg['level'] != new_val:
            base.db.FindOneAndUpdate('settings', 'readings',{'name' : reading_name},
                    {'$set' : {f'config.{rm}.level': new_val}})
            base.db.LogUpdate(name=sensor,
                              reading=reading_name,
                              key=f'config.{rm}.level',
                              value=new_val,
                              **user)

    return redirect('/pancake/detail/')

@require_POST
def change_default(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    info = request.POST
    new_values = request.POST
    host = new_values['host_name']
    if host not in base.db.Distinct('common', 'hosts', 'hostname'):
        return redirect('/pancake/hosts/')
    old_values = base.db.GetHostSetting(host)
    if new_values['sysmon_timer'] != old_values['sysmon_timer']:
        base.db.SetHostSetting(host, set={'sysmon_timer': int(new_values['sysmon_timer'])})
    new_default = []
    for parameter in new_values.keys():
        if parameter.startswith('checkbox'):
            new_default.append(new_values[parameter])
    base.db.SetHostSetting(host, set={'default':new_default})
    return redirect('/pancake/hosts')

@require_POST
def update_shift(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    info = request.POST
    user = base.client(request.META)
    shift_key = info['shift_key']
    shifters = [info[k] if info[k] != 'None' else '' for k in ['primary', 'secondary1', 'secondary2']]
    base.db.updateDatabase('settings','shifts', cuts={'shift_key' : shift_key},
            updates = {'$set' : {'shifters' : shifters}})
    base.db.LogUpdate(field='contacts', shift_key=shift_id, shifters=shifters, **user)
    return redirect('/pancake/contacts/')

@require_POST
def add_new_contact(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    info = request.POST
    user = base.client(request.META)
    contact = {'name' : info['firstname'] + info['lastname'][0],
            'email' : info['email'],
            'sms' : info['sms'],
            'status' : -1,
            'first_name' : info['firstname'],
            'last_name' : info['lastname'],
            }
    base.db.insertIntoDatabase('settings','contacts',contact)
    base.db.LogUpdate(field='contacts', new=info['firstname'] + info['lastname'][0], **user)
    return redirect('/pancake/contacts/')

@require_POST
def scram(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    for ch in range(12):
        base.dispatcher.ProcessCommand(f'caen_sy5527 set ch{ch} pdn 1')
        base.dispatcher.ProcessCommand(f'caen_sy5527 set ch{ch} pw 0')
    return HttpResponseNotModified()

@require_POST
def update_pmts(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/pancake/')
    new_values = request.POST
    user = base.client(request.META)
    is_digital = {'setp' : False, 'tripi' : False, 'tript' : False, 'rup' : False,
            'rdn' : False, 'pon' : True, 'pdn' : True, 'pw' : True}
    digital_map = {'On' : 1, 'Off' : 0, 'En' : 1, 'Dis' : 0, 'Ramp' : 1, 'Kill' : 0}
    last_vals = views_get.get_latest_values()
    for ch in range(12):
        for quant in ['setp', 'tripi', 'tript', 'rup', 'rdn', 'pon', 'pdn', 'pw']:
            key = f'{quant}_{ch}'
            new_val = request.POST[f'ch{ch}_{quant}']
            last_val = last_vals[key]['value']
            if is_digital[quant] and digital_map[new_val] != last_val:
                doc = {'command' : f'set ch{ch} sl3 {quant} {digital_map[new_val]}',
                        'name' : 'caen_sy5527'}
                doc.update(user)
                base.db.LogCommand(doc)
            elif quant == 'setp' and not isclose(float(new_val), last_val):
                doc = {'command' : f'set ch{ch} sl3 vset {new_val}',
                        'name' : 'caen_sy5527'}
                doc.update(user)
                base.db.LogCommand(doc)
            elif not is_digital[quant] and not isclose(float(new_val), last_val):
                doc = {'command' : f'set ch{ch} sl3 {quant} {new_val}',
                        'name' : 'caen_sy5527'}
                doc.update(user)
                base.db.LogCommand(doc)
    return redirect('/pancake/caen_hv/')
