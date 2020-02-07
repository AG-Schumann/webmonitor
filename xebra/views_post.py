from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from Doberman import dispatcher
import datetime

from . import base

@require_POST
def startstop(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    name = request.POST['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return redirect('detail')
    status = base.db.GetSensorSetting(name, 'status')
    user = base.client(request.META)
    if status == 'online':
        dispatcher.ProcessCommand(base.db, f'stop {name}', user=user)
    elif status == 'offline':
        dispatcher.ProcessCommand(base.db, f'start {name}' % name, user=user)
    return redirect('detail')

@require_POST
def change_address(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    new_vals = request.POST
    name = new_vals['sensor_name']
    if name not in base.db.Distinct('settings','sensors','name'):
        return redirect('detail')
    old_vals = base.db.GetSensorSetting(name, 'address')
    if old_vals is None:
        return redirect('detail')
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
    return redirect('detail')

@require_POST
def log_command(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    user = base.client(request.META)
    dispatcher.ProcessCommand(base.db,request.POST['command'], user=user)
    return redirect('detail')

@require_POST
def change_reading(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    new_vals = request.POST
    sensor = new_vals['sensor_name']
    if sensor not in base.db.Distinct('settings','sensors','name'):
        return redirect('detail')
    reading_name = new_vals['reading_name']
    old_vals = base.db.GetReadingSetting(sensor, reading_name)
    if old_vals is None:
        return redirect('detail')
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
    alarms = []
    levels = {}
    for key in new_vals.keys():
        if "__" in key:
            parts = key.split("__")
            ty = parts[0]
            parameter = parts[1]
            if parameter.startswith('al'):
                try:
                    levels[ty][parameter] = new_vals[key]
                except KeyError:
                    levels[ty] = {}
                    levels[ty][parameter] = new_vals[key]
                continue
            this_type = list(filter(lambda dict: dict['type'] == ty, alarms))
            if this_type == []:
                alarms.append({'type': ty, parameter: float(new_vals[key])})
            else:
               this_type[0][parameter] = float(new_vals[key])
    for ty in levels.keys():
        level_list = []
        if len(list(levels[ty].keys())[0].split('_')) == 3: #levels of form [[ , ],[ , ], ...]
            for i in range(int(len(levels[ty])/2)):
                level_list.append([float(levels[ty][f'al_{i}_0']),float(levels[ty][f'al_{i}_1'])])
        else:
            for i in range(len(levels[ty])):
                level_list.append(levels[ty][f'al_{i}'])
        this_type = list(filter(lambda dict: dict['type'] == ty, alarms))
        this_type[0]['levels'] = level_list
        
    for alarm in alarms:
        base.db.UpdateAlarm(reading_name, alarm)

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

    return redirect('detail')

@require_POST
def change_default(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    info = request.POST
    new_values = request.POST
    host = new_values['host_name']
    if host not in base.db.Distinct('common', 'hosts', 'hostname'):
        return redirect('hosts')
    old_values = base.db.GetHostSetting(host)
    if new_values['sysmon_timer'] != old_values['sysmon_timer']:
        base.db.SetHostSetting(host, set={'sysmon_timer': int(new_values['sysmon_timer'])})
    new_default = []
    for parameter in new_values.keys():
        if parameter.startswith('checkbox'):
            new_default.append(new_values[parameter])
    base.db.SetHostSetting(host, set={'default':new_default})
    return redirect('hosts')

@require_POST
def update_shift(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    info = request.POST
    user = base.client(request.META)
    shift_key = info['shift_key']
    shifters = [info[k] if info[k] != 'None' else '' for k in ['primary', 'secondary1', 'secondary2']]
    base.db.updateDatabase('settings','shifts', cuts={'shift_key' : shift_key},
            updates = {'$set' : {'shifters' : shifters}})
    base.db.LogUpdate(field='contacts', shift_key=shift_id, shifters=shifters, **user)
    return redirect('contacts')

@require_POST
def add_new_contact(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
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
    return redirect('contacts')

@require_POST
def delete_alarm(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    print('GAGAGAG')
    print(request.POST)
    #base.db.DeleteAlarm('temp_ts_top', 'timesince')
    return redirect('detail')

@require_POST
def scram(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    for ch in range(12):
        base.dispatcher.ProcessCommand(f'caen_sy5527 set ch{ch} pdn 1')
        base.dispatcher.ProcessCommand(f'caen_sy5527 set ch{ch} pw 0')
    return HttpResponseNotModified()

@require_POST
def update_pmts(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('index')
    new_values = request.POST
    user = base.client(request.META)
    is_digital = {'setp' : False, 'tripi' : False, 'tript' : False, 'rup' : False,
            'rdn' : False, 'pon' : True, 'pdn' : True, 'pw' : True}
    digital_map = {'On' : 1, 'Off' : 0, 'En' : 1, 'Dis' : 0, 'Ramp' : 1, 'Kill' : 0}
    for ch in range(12):
        for quant in ['setp', 'tripi', 'tript', 'rup', 'rdn', 'pon', 'pdn', 'pw']:
            key = f'{quant}_{ch}'
            newval = request.POST[f'ch{ch}_{quant}']
            last_val = base.db.readFromDatabase('data', 'caen_sy5527',
                    {key : {'$exists' : 1}}, onlyone=True, sort=[('_id', -1)])[key]
            if is_digital[quant] and digital_map[newval] != last_val:
                doc = {'command' : f'set ch{ch} sl3 {quant} {digital_map[newval]}',
                        'name' : 'caen_sy5527'}
                doc.update(user)
                base.db.LogCommand(doc)
            elif new_val != last_val:
                doc = {'command' : f'set ch{ch} sl3 {quant} {newval}',
                        'name' : 'caen_sy5527'}
                doc.update(user)
                base.db.LogCommand(doc)
    return HttpResponseNotModified()
