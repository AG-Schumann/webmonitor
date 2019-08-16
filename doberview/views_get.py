from django.http import JsonResponse, HttpResponseNotModified
from django.views.decorators.http import require_GET

from . import base
import datetime
from urllib.parse import unquote


@require_GET
def getalarms(request):
    docs = []
    sort = [('when', -1)]
    try:
        for row in base.db.readFromDatabase('logging', 'alarm_history', sort=sort, limit=10):
            docs.append({
                'when' : row['when'].strftime("%Y-%m-%d %H:%M:%S"),
                'name' : row['name'],
                'message' : row['msg'].replace("<","").replace(">",""),
                })
        return JsonResponse({'docs' : docs})
    except Exception as e:
        print("getalarms: %s" % e)
        return JsonResponse({'docs' : []})

@require_GET
def getlogs(request):
    docs = []
    levels = {
            10 : 'debug',
            20 : 'info',
            30 : 'warning',
            40 : 'error',
            50 : 'critical',
        }
    sort = [('when', -1)]
    try:
        for row in base.db.readFromDatabase('logging', 'logs', sort=sort, limit=10):
            docs.append({
                'when' : row['when'].strftime("%Y-%m-%d %H:%M:%S"),
                'level' : levels[int(row['level'])],
                'name' : row['name'],
                'message' : row['msg'].replace("<","").replace(">",""),
            })
        return JsonResponse({'docs' : docs})
    except Exception as e:
        print('getlogs: %s' % e)
        return JsonResponse({'docs' : []})

@require_GET
def get_sensor_details(request, sensor_name=""):
    ret = {'html' : {}, 'value' : {}}
    if sensor_name not in base.db.Distinct('settings','sensors','name'):
        return JsonResponse(ret)
    sensor_doc = base.db.GetSensorSettings(sensor_name)
    ret['value']['s_name_startstop'] = sensor_name
    ret['value']['s_name_rd'] = sensor_name
    ret['value']['s_name_addr'] = sensor_name
    ret['html']['subtitle'] = "Sensor detail: " + sensor_name

    ret['html']['reading_dropdown'] = '<option value="" selected>Select reading</option>'
    for reading_name in sensor_doc['readings']:
        ret['html']['reading_dropdown'] += f'<option value="{reading_name}">{reading_name}</option>'

    if sensor_doc['status'] == 'online':
        ret['value']['startbtn'] = 'Stop'
        ret['html']['startbtn'] = 'Stop'
        ret['html']['status_legend'] = 'Hardware connection online'
    elif sensor_doc['status'] == 'offline':
        ret['value']['startbtn'] = 'Start'
        ret['html']['startbtn'] = 'Start'
        ret['html']['status_legend'] = 'Hardware connection offline'
    else:
        ret['value']['startbtn'] = ''
        ret['html']['startbtn'] = ''
        ret['html']['status_legend'] = 'Hardware connection unknown'

    if 'address' in sensor_doc:
        s = ''
        s += '<legend>Addressing</legend>'
        if 'ip' in sensor_doc['address']:
            s += f'IP: <input type="text" name="ip" value="{sensor_doc["address"]["ip"]}"'
            s += r' pattern="\\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\b">'
            s += '<br>'
            s += f'Port: <input type="number" name="port" value="{int(sensor_doc["address"]["port"])}" step="1">'
            s += '<br>'
        if 'tty' in sensor_doc['address']:
            s += f'SerialID: <input type="text" name="serialID" value="{sensor_doc["address"]["serialID"]}">'
            s += '<br>'
            s += f'Serial address: <input type="text" name="tty" value="{sensor_doc["address"]["tty"]}" '
            s += r'pattern="\\b(?:(?:USB|S)[1-9]?[0-9])\\b">'
            s += '<br>'
            s += f'Baud: <select name="baud">'
            for baud in [9600,19200,38400,57600]:
                selected = 'selected' if sensor_doc['address']['baud'] == baud else ''
                s += f'<option value="{baud}" {selected}>{baud}</option>'
            s += '</select>'
            s += '<br>'
        if len(s) > 27: # magic number
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
    ret = {'html' : {}, 'value' : {}}
    if sensor_name not in base.db.Distinct('settings','sensors','name'):
        return HttpResponseNotModified()
    readings = base.db.GetSensorSetting(sensor_name, 'readings')
    if reading_name not in readings:
        return HttpResponseNotModified()
    reading = base.db.GetReading(sensor_name, reading_name)
    ret['html']['rd_legend'] = "%s" % (reading['description'])
    ret['value']['rd_name'] = reading['name']
    ret['value']['rd_alrec'] = str(int(reading['recurrence']))
    ret['value']['rd_roi'] = str(int(reading['readout_interval']))

    ret['html']['rd_alarm_list'] = ''
    for i,(lo,hi) in enumerate(reading['alarms']):
        ret['html']['rd_alarm_list'] += f'<li>Level {i}: Low:<input type="number" name="al_{i}_0" value="{lo}" step="any"> High:<input type="number" name="al_{i}_1" value="{hi}" step="any"></li>'
    ret['html']['rd_cfg_list'] = ''
    for rm,cfg in reading['config'].items():
        ret['html']['rd_cfg_list'] += f'<li>{rm}: <input type="number" min="-1" step=1 max="{len(reading["alarms"])-1}" value="{int(cfg["level"])}" name="{rm}_level"></li>'
    ret['html']['rd_runmode'] = ''
    for rm in ['default','testing','recovery']:
        selected = 'selected' if rm == reading['runmode'] else ''
        ret['html']['rd_runmode'] += f'<option value="{rm}" {selected}>{rm}</option>'
    ret['html']['rd_status'] = ''
    for status in ['offline','online']:
        selected = 'selected' if status == reading['status'] else ''
        ret['html']['rd_status'] += f'<option value="{status}" {selected}>{status}</option>'

    return JsonResponse(ret)

@require_GET
def getreadings(request, name):
    if name not in base.db.Distinct('settings','sensors','name'):
        ret = {'readings' : []}
    else:
        ret = {'readings' : base.db.Distinct('settings', 'sensors',
            'readings.description', {'name' : name})}
    return JsonResponse(ret)

@require_GET
def getoverview(request):
    tabs = {}
    status_docs = base.db.GetCurrentStatus()

    for sensor_name, status_doc in status_docs.items():
        if status_doc['status'] == 'offline':
            tabs['%s_head' % sensor_name] = sensor_name
            tabs['%s_body' % sensor_name] = '<td colspan="5" style="color:#DD0000">Offline</td>'
        else:
            tabs['%s_head' % sensor_name] = '%s: last heartbeat %i seconds ago' % (
                    sensor_name, status_doc['last_heartbeat'])
            key = '%s_body' % sensor_name
            tabs[key] = '<tr>'
            for reading_name, reading_doc in status_doc['readings'].items():
                tabs[key] += f'<td>{reading_doc["description"]}</td>'
                if reading_doc['status'] == 'online':
                    tabs[key] += f'<td>{reading_doc["last_time"]:.1f} sec</td>'
                    tabs[key] += f'<td>{reading_doc["last_value"]:.3g}</td>'
                    tabs[key] += f'<td>{reading_doc["runmode"][0]}</td>'
                else:
                    tabs[key] += '<td colspan="3" style="color:#FF7F00">Offline</td>'
                tabs[key] += '</tr><tr>'
            tabs[key] = tabs[key][:-4]
    return JsonResponse(tabs)

@require_GET
def get_shifts(request, start, end):
    start = datetime.datetime.fromisoformat(start)
    end = datetime.datetime.fromisoformat(end)
    shifts = []
    for shift in base.db.readFromDatabase('settings','shifts',
            {'end' : {'$gte' : start},
              'start' : {'$lte' : end}}):
        shifts.append({
            'id' : shift['key'],
            'start' : shift['start'].isoformat(),
            'end' : shift['end'].isoformat(),
            'editable' : False,
            'title' : 'Primary: %s; Secondary: %s, %s' % tuple(shift['shifters'])
            })

    return JsonResponse({'events' : shifts})

def get_shift_detail(request, date):
    shift = base.db.readFromDatabase('settings','shifts',
            {'key' : date}, onlyone=True)
    if shift is None:
        return JsonResponse({})
    return JsonResponse({'primary' : shift['shifters'][0],
        'secondary1' : shift['shifters'][1],
        'secondary2' : shift['shifters'][2],
        'start' : shift['start'].isoformat(sep=' ')[:16],
        'end' : shift['end'].isoformat(sep=' ')[:16],
        })
