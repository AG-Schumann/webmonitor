from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from Doberman import dispatcher
import datetime
from math import isclose
from . import views_get
from . import base


@require_POST
def change_address(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    new_vals = request.POST
    name = new_vals['sensor_name']
    if name not in base.db.distinct('settings', 'sensors', 'name'):
        return redirect('/xebra/detail/')
    old_vals = base.db.get_sensor_setting(name, 'address')
    if old_vals is None:
        return redirect('/xebra/detail/')
    user = base.client(request.META)
    if 'ip' in old_vals:
        if new_vals['ip'] != old_vals['ip']:
            base.db.set_sensor_setting(name, 'address.ip', new_vals['ip'])
            base.db.log_update(name=name,
                               key='address.ip',
                               value=new_vals['ip'],
                               **user)
        elif int(new_vals['port']) != old_vals['port']:
            base.db.set_sensor_setting(name, 'address.port', int(new_vals['port']))
            base.db.log_update(name=name,
                               key='address.port',
                               value=int(new_vals['port']),
                               **user)
    if 'tty' in old_vals:
        if new_vals['tty'] != old_vals['tty']:
            base.db.set_sensor_setting(name, 'address.tty', new_vals['tty'])
            base.db.log_update(name=name,
                               key='address.tty',
                               value=new_vals['tty'],
                               **user)
        elif new_vals['serialID'] != old_vals['serialID']:
            base.db.set_sensor_setting(name, 'address.serialID', new_vals['serialID'])
            base.db.log_update(name=name,
                               key='address.serialID',
                               value=new_vals['serialID'],
                               **user)
        elif 'baud' in old_vals and int(new_vals['baud']) != old_vals['baud']:
            base.db.set_sensor_setting(name, 'address.baud', int(new_vals['baud']))
            base.db.log_update(name=name,
                               key='address.baud',
                               value=int(new_vals['baud']),
                               **user)
    return redirect('/xebra/detail/')


@require_POST
def log_command(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    user = base.client(request.META)
    command = f'{request.POST["sensor_name"]} {request.POST["command"]}'
    dispatcher.process_command(base.db, command, user=user)
    return redirect('/xebra/detail/')


@require_POST
def change_reading(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    new_vals = request.POST
    sensor = new_vals['sensor_name']
    if sensor not in base.db.distinct('settings', 'sensors', 'name'):
        return redirect('/xebra/detail/')
    reading_name = new_vals['reading_name']
    old_vals = base.db.get_reading_setting(sensor, reading_name)
    if old_vals is None:
        return redirect('/xebra/detail/')
    user = base.client(request.META)
    for key, func in zip(['status', 'readout_interval', 'runmode'],
                         [str, int, str]):
        new_val = func(new_vals[key])  # django doesn't typecast
        if old_vals[key] != new_vals:
            base.db.set_reading_setting(sensor, reading_name, key, new_val)
            base.db.log_update(name=sensor,
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
                    # alarm levels for pid and simple
                    levels[parameter[3:]] = float(new_vals[key])
                elif parameter.startswith('max_duration'):
                    # alarm levels for time_since
                    max_duration[parameter[13:]] = float(new_vals[key])
                elif parameter == 'enabled':
                    new_alarm[parameter] = new_vals[key]
                else:
                    new_alarm[parameter] = float(new_vals[key])
        if len(levels) > 0:
            new_levels = []
            for i in range(len(levels) // 2):
                new_levels.append([levels[f'{i}_0'], levels[f'{i}_1']])
            new_alarm['levels'] = new_levels
        if len(max_duration) > 0:
            new_max_d = []
            for i in range(len(max_duration)):
                new_max_d.append(max_duration[f'{i}'])
            new_alarm['max_duration'] = new_max_d
        if new_alarm != old_alarm:
            base.db.update_alarm(reading_name, new_alarm)

    return redirect('/xebra/detail/')


@require_POST
def change_default(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    new_values = request.POST
    host = new_values['host_name']
    if host not in base.db.distinct('common', 'hosts', 'hostname'):
        return redirect('/xebra/hosts')
    old_values = base.db.get_host_setting(host)
    if new_values['sysmon_timer'] != old_values['sysmon_timer']:
        base.db.set_host_setting(host, set={'sysmon_timer': int(new_values['sysmon_timer'])})
    new_default = []
    for parameter in new_values.keys():
        if parameter.startswith('checkbox'):
            new_default.append(new_values[parameter])
    base.db.set_host_setting(host, set={'default': new_default})
    return redirect('/xebra/hosts')


@require_POST
def change_aggregation(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    new_values = request.POST
    name = new_values['agg_name']
    operation = new_values['operation']
    time_window = new_values['time_window']
    alarms_count = 0
    for key in new_values.keys():
        if key[-2:] == "rd":
            alarms_count += 1
    alarms = []
    for i in range(alarms_count):
        rd = new_values[f'{i}_rd']
        ty = new_values[f'{i}_type']
        if (rd or ty) == "none":
            return redirect('/xebra/alarms')
        alarms.append(rd + ',' + ty)
    doc = {'name': name, 'operation': operation, 'time_window': time_window, 'alarms': alarms}
    if name in base.db.distinct('settings', 'alarm_aggregations', 'name'):
        base.db.find_one_and_update('settings', 'alarm_aggregations', {'name': name}, {'$set': {'operation': operation}})
        base.db.find_one_and_update('settings', 'alarm_aggregations', {'name': name},
                                 {'$set': {'time_window': time_window}})
        base.db.find_one_and_update('settings', 'alarm_aggregations', {'name': name}, {'$set': {'alarms': alarms}})
    else:
        # add new aggregation
        print()
    return redirect('/xebra/alarms')


@require_POST
def update_shift(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    info = request.POST
    user = base.client(request.META)
    shift_key = info['shift_key']
    shifters = [info[k] if info[k] != 'None' else '' for k in ['primary', 'secondary1', 'secondary2']]
    base.db.find_one_and_update('settings', 'shifts', {'key': shift_key}, {'$set': {'shifters': shifters}})
    base.db.log_update(field='contacts', shift_key=shift_key, shifters=shifters, **user)
    return redirect('/xebra/contacts')


@require_POST
def add_new_contact(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    info = request.POST
    user = base.client(request.META)
    contact = {'name': info['firstname'] + info['lastname'][0],
               'email': info['email'],
               'sms': info['sms'],
               'status': -1,
               'first_name': info['firstname'],
               'last_name': info['lastname'],
               }
    base.db.insert_into_db('settings', 'contacts', contact)
    base.db.log_update(field='contacts', new=info['firstname'] + info['lastname'][0], **user)
    return redirect('/xebra/contacts')


@require_POST
def scram(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    user = base.client(request.META)
    for ch in range(12):
        dispatcher.ProcessCommand(base.db, f'caen_sy5527 set ch{ch} pdn 1', user=user)
        dispatcher.ProcessCommand(base.db, f'caen_sy5527 set ch{ch} pw 0', user=user)
    return redirect('/xebra/caen_hv')


@require_POST
def update_pmts(request):
    if not base.is_schumann_subnet(request.META):
        return redirect('/xebra/error')
    new_values = request.POST
    user = base.client(request.META)
    is_digital = {'setp': False, 'tripi': False, 'tript': False, 'rup': False,
                  'rdn': False, 'pon': True, 'pdn': True, 'pw': True}
    digital_map = {'On': 1, 'Off': 0, 'En': 1, 'Dis': 0, 'Ramp': 1, 'Kill': 0}
    last_vals = views_get.get_latest_values()
    for ch in range(12):
        for quant in ['setp', 'tripi', 'tript', 'rup', 'rdn', 'pon', 'pdn', 'pw']:
            key = f'{quant}_{ch}'
            new_val = request.POST[f'ch{ch}_{quant}']
            last_val = last_vals[key]['value']
            if is_digital[quant] and digital_map[new_val] != last_val:
                doc = {'command': f'set ch{ch} sl3 {quant} {digital_map[new_val]}',
                       'name': 'caen_sy5527'}
                doc.update(user)
                base.db.log_command(doc)
            elif quant == 'setp' and not isclose(float(new_val), last_val):
                doc = {'command': f'set ch{ch} sl3 vset {new_val}',
                       'name': 'caen_sy5527'}
                doc.update(user)
                base.db.log_command(doc)
            elif not is_digital[quant] and not isclose(float(new_val), last_val):
                doc = {'command': f'set ch{ch} sl3 {quant} {new_val}',
                       'name': 'caen_sy5527'}
                doc.update(user)
                base.db.log_command(doc)
    return redirect('/xebra/caen_hv')
