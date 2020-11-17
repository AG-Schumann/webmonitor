from django.http import JsonResponse, HttpResponseNotModified
from django.views.decorators.http import require_GET
from influxdb import InfluxDBClient
from . import base
import datetime
from datetime import datetime as dt


@require_GET
def get_alarms(request):
    docs = []
    sort = [('_id', -1)]
    try:
        for row in base.db.read_from_db('logging', 'alarm_history', sort=sort, limit=10):
            docs.append({
                'when': dt.fromtimestamp(int(str(row['_id'])[:8], 16)).strftime("%Y-%m-%d %H:%M:%S"),
                'message': row['msg'].replace("<", "").replace(">", ""),
            })
        return JsonResponse({'docs': docs})
    except Exception as e:
        print("getalarms: %s" % e)
        return JsonResponse({'docs': []})


@require_GET
def get_logs(request):
    docs = []
    levels = {
        10: 'debug',
        20: 'info',
        30: 'warning',
        40: 'error',
        50: 'critical',
    }
    sort = [('_id', -1)]
    try:
        for row in base.db.read_from_db('logging', 'logs', sort=sort, limit=10):
            docs.append({
                'when': dt.fromtimestamp(int(str(row['_id'])[:8], 16)).strftime("%Y-%m-%d %H:%M:%S"),
                'level': levels[int(row['level'])],
                'name': row['name'],
                'message': row['msg'].replace("<", "").replace(">", ""),
            })
        return JsonResponse({'docs': docs})
    except Exception as e:
        print('getlogs: %s' % e)
        return JsonResponse({'docs': []})


@require_GET
def get_sensor_details(request, sensor_name=""):
    ret = {'html': {}, 'value': {}}
    if sensor_name not in base.db.distinct('settings', 'sensors', 'name'):
        return JsonResponse(ret)
    sensor_doc = base.db.get_sensor_setting(sensor_name)
    ret['value']['s_name_startstop'] = sensor_name
    ret['value']['s_name_rd'] = sensor_name
    ret['value']['s_name_addr'] = sensor_name
    ret['html']['subtitle'] = "Sensor detail: " + sensor_name

    ret['html']['reading_dropdown'] = '<option value="" selected>Select reading</option>'
    for reading_name in sensor_doc['readings']:
        ret['html']['reading_dropdown'] += f'<option value="{reading_name}">{reading_name}</option>'

    if 'address' in sensor_doc:
        s = ''
        s += '<legend>Addressing</legend>'
        if 'ip' in sensor_doc['address']:
            s += f'IP: <input type="text" name="ip" value="{sensor_doc["address"]["ip"]}"'
            s += r' pattern="((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)">'
            s += '<br>'
            s += f'Port: <input type="number" name="port" value="{int(sensor_doc["address"]["port"])}" step="1">'
            s += '<br>'
        if 'tty' in sensor_doc['address']:
            s += f'SerialID: <input type="text" name="serialID" value="{sensor_doc["address"]["serialID"]}">'
            s += '<br>'
            s += f'Serial address: <input type="text" name="tty" value="{sensor_doc["address"]["tty"]}" '
            s += r'pattern="(?:(?:USB|S)[1-9]?[0-9])">'
            s += '<br>'
            s += f'Baud: <select name="baud">'
            for baud in [9600, 19200, 38400, 57600]:
                selected = 'selected' if sensor_doc['address']['baud'] == baud else ''
                s += f'<option value="{baud}" {selected}>{baud}</option>'
            s += '</select>'
            s += '<br>'
        if len(s) > 27:  # magic number
            s += '<button type="submit" value="Submit">Submit</button>'
            s += '<button type="reset" value="Reset">Reset</button>'
        else:
            s += 'No address info!'
        ret['html']['address_block'] = s
    else:
        ret['html']['address_block'] = 'No address info!'

    return JsonResponse(ret)


@require_GET
def get_reading_detail(request, sensor_name="", reading_name=""):
    ret = {'html': {}, 'value': {}}
    if sensor_name not in base.db.distinct('settings', 'sensors', 'name'):
        return HttpResponseNotModified()
    readings = base.db.get_sensor_setting(sensor_name, 'readings')
    if type(readings) is dict:
        readings = list(readings.keys())
    if reading_name not in readings:
        return HttpResponseNotModified()
    reading = base.db.get_reading_setting(sensor_name, reading_name)
    ret['html']['rd_legend'] = "%s" % (reading['description'])
    ret['value']['rd_name'] = reading['name']
    ret['value']['rd_roi'] = str(int(reading['readout_interval']))

    alarms = reading['alarms']
    for alarm in alarms:
        al_type = alarm["type"]
        enabled = alarm["enabled"]
        ret['value'][f'{al_type}_enabled'] = enabled
        ret['html'][f'{al_type}_body'] = ""
        for parameter in alarm.keys():
            if parameter == 'type' or parameter == 'enabled':
                continue
            ret['html'][f'{al_type}_body'] += f'<tr><td align="left"> {parameter} </td>'
            if parameter == 'levels':
                ret['html'][f'{al_type}_body'] += '<td>'
                for i, (lo, hi) in enumerate(alarm['levels']):
                    ret['html'][
                        f'{al_type}_body'] += f'<li>Level {i}: Low:<input type="number" name="{al_type}__al_{i}_0" value="{lo}" step="any"> High:<input type="number" name="{al_type}__al_{i}_1" value="{hi}" step="any"></li>'
                ret['html'][f'{al_type}_body'] += '</td></tr>'
            elif parameter == 'max_duration':
                ret['html'][f'{al_type}_body'] += '<td>'
                for i, val in enumerate(alarm['max_duration']):
                    ret['html'][
                        f'{al_type}_body'] += f'<li>Level {i}:<input type="number" name="{al_type}__max_duration_{i}" value="{val}" step="any"></li>'
            else:
                ret['value'][f'{al_type}_{parameter}'] = alarm[parameter]
                ret['html'][
                    f'{al_type}_body'] += f'<td align="left"> <input type="number" min="0" max="1000" step="1" id="{al_type}_{parameter}" name="{al_type}__{parameter}" ></tr>'

    ret['html']['rd_cfg_list'] = ''
    for rm, cfg in reading['config'].items():
        ret['html'][
            'rd_cfg_list'] += f'<li>{rm}: <input type="number" min="-1" step=1 max="{len(reading["alarms"]) - 1}" value="{int(cfg["level"])}" name="{rm}_level"></li>'

    ret['html']['rd_runmode'] = ''
    for rm in ['default', 'testing', 'recovery']:
        selected = 'selected' if rm == reading['runmode'] else ''
        ret['html']['rd_runmode'] += f'<option value="{rm}" {selected}>{rm}</option>'

    ret['html']['rd_status'] = ''
    for status in ['offline', 'online']:
        selected = 'selected' if status == reading['status'] else ''
        ret['html']['rd_status'] += f'<option value="{status}" {selected}>{status}</option>'

    return JsonResponse(ret)


@require_GET
def get_host_detail(request, host_name=""):
    ret = {'html': {}, 'value': {}}
    if host_name not in base.db.distinct('common', 'hosts', 'hostname'):
        return HttpResponseNotModified()
    doc = base.db.get_host_setting(host_name)
    ret['value']['sysmon_timer'] = doc['sysmon_timer']
    default = doc['default']
    ret['value']['host_name'] = host_name
    ret['html'][
        'grafana'] = f'http://10.4.73.172:3000/d/WzsbkBwWk/system-mon?refresh=5s&kiosk=tv&var-hostname={host_name}'
    ret['html']['host_legend'] = host_name
    ret['html']['default_table'] = '<tr><td colspan="2">Default</td></tr>'
    for sensor in default:
        ret['html']['default_table'] += f'<tr><td>{sensor}</td>'
        ret['html'][
            'default_table'] += f'<td><input type="checkbox" name="checkbox_{sensor}" value="{sensor}" checked></td></tr>'
    unmonitored = base.db.get_unmonitored_sensors()
    ret['html']['unmonitored_table'] = '<tr><td colspan="2">Unmonitored</td></tr>'
    for sensor in unmonitored:
        ret['html']['unmonitored_table'] += f'<tr><td>{sensor}</td>'
        ret['html'][
            'unmonitored_table'] += f'<td><input type="checkbox" name="checkbox_{sensor}" value="{sensor}"></td></tr>'
    return JsonResponse(ret)


@require_GET
def get_overview(request):
    tabs = {}
    status_docs = base.db.get_current_status()
    latest_values = get_latest_values()
    for hostname, status_doc in status_docs.items():
        if status_doc['status'] == 'offline':
            tabs[f'{hostname}_head'] = f'{hostname}'
            tabs[f'{hostname}_body'] = '<td colspan="4" style="color:#FF0000">Offline</td>'
        else:
            tabs[f'{hostname}_head'] = f'{hostname}: last heartbeat {status_doc["last_heartbeat"]:.1f} seconds ago'
            key = f'{hostname}_body'
            tabs[key] = '<tr>'
            for sensor_name, sensor_doc in status_doc['sensors'].items():
                tabs[
                    key] += f'<td colspan="4" style="background-color:#7395AE; color:#ffffff">{sensor_name}: last heartbeat {sensor_doc["last_heartbeat"]:.1f} seconds ago</td>'
                tabs[key] += '<tr><td style="background-color:#7395AE; color:#ffffff">Description</td>'
                tabs[key] += '<td style="background-color:#7395AE; color:#ffffff">Value</td>'
                tabs[key] += '<td style="background-color:#7395AE; color:#ffffff">Time</td>'
                tabs[key] += '<td style="background-color:#7395AE; color:#ffffff">Runmode</td></tr>'
                for reading_name, reading_doc in sensor_doc['readings'].items():
                    tabs[key] += '<tr>'
                    tabs[key] += f'<td> {reading_doc["description"]} </td>'
                    if reading_doc["status"] == "online":
                        tabs[key] += f'<td> {latest_values[reading_name]["value"]:.3g} </td>'
                        tabs[key] += f'<td> {latest_values[reading_name]["time"]:.1f} sec</td>'
                        tabs[key] += f'<td> {reading_doc["runmode"][0]} </td>'
                    else:
                        tabs[key] += '<td colspan=3 style="color:#FF0000">Offline</td>'
                    tabs[key] += '</tr><tr>'
                tabs[key] = tabs[key][:-4]
                tabs[key] += '</tr><tr class="blank_row"><td colspan="4"></td></tr><tr>'
            tabs[key] = tabs[key][:-4]
    return JsonResponse(tabs)


@require_GET
def get_shifts(request, start, end):
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)
    shifts = []
    for shift in base.db.read_from_database('settings', 'shifts',
                                            {'end': {'$gte': start},
                                             'start': {'$lte': end}}):
        shifts.append({
            'id': shift['key'],
            'start': shift['start'].isoformat(),
            'end': shift['end'].isoformat(),
            'editable': False,
            'title': 'Primary: %s; Secondary: %s, %s' % tuple(shift['shifters'])
        })

    return JsonResponse({'events': shifts})


@require_GET
def get_shift_detail(request, date):
    shift = base.db.read_from_database('settings', 'shifts',
                                       {'key': date}, onlyone=True)
    if shift is None:
        return JsonResponse({})
    return JsonResponse({'primary': shift['shifters'][0],
                         'secondary1': shift['shifters'][1],
                         'secondary2': shift['shifters'][2],
                         'start': shift['start'].isoformat(sep=' ')[:16],
                         'end': shift['end'].isoformat(sep=' ')[:16],
                         })


@require_GET
def get_pmts(request, speed='slow'):
    latest_values = get_latest_values()

    def fields(ch):
        f = [f'stat_{ch}', f'vmon_{ch}', f'imon_{ch}', f'setp_{ch}', f'tript_{ch}',
             f'tripi_{ch}', f'rup_{ch}', f'rdn_{ch}', f'pon_{ch}', f'pdn_{ch}',
             f'pw_{ch}']
        return f

    ret = {}
    for ch in range(12):
        for f in fields(ch):
            ret[f] = latest_values[f]['value']
    return JsonResponse(ret)


def get_latest_values():
    client = InfluxDBClient(host='192.168.131.2', port=8086, database='pancake')
    latest_values = {}
    measurements = [d['name'] for d in client.get_list_measurements()]
    for measurement in measurements:
        if measurement == "sysmon":
            continue
        key_set = client.query(f"SHOW FIELD KEYS FROM {measurement}")
        keys = [d['fieldKey'] for d in list(key_set.get_points())]
        for key in keys:
            latest_values[key] = {}
            result_set = client.query(f"SELECT time, {key} FROM {measurement} ORDER BY time DESC LIMIT 1", epoch="ms")
            result = dict(list(result_set.get_points())[0])
            latest_values[key]['time'] = dt.now().timestamp() - (result['time'] / 1000)
            latest_values[key]['value'] = result[key]

    return latest_values
