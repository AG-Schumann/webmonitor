from django.http import JsonResponse, HttpResponseNotModified
from django.views.decorators.http import require_GET

from . import base


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
        ret['html']['rd_cfg_list'] += f'<li>{rm}: <input type="number" min="-1" step=1 max="{len(reading["alarms"])-1}" value="{cfg["level"]}" name="{rm}_level"></li>'
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
def getdata(request, *args):
    """
    Pulls data for one chart from the database, returns an object
    to be passed directly to plotly
    """
    #start_time = base.db.GetField()  # TODO finish
    start_time = datetime.datetime(2019,2,18,0,0,0)
    names = base.db.Distinct('settings','sensors','name')
    data = []
    num_pts = 40000  # max number of points to plot
    decimate_after = 3600  # data older than this many seconds is decimated
    colors = ['rgb(0,0,220)','rgb(0,220,0)', 'rgb(220,0,0)']
    earliest_t = 0
    layout = {
            'xaxis' : {'type' : 'log', 'autorange' : False,
                'title' : '<-- then | Time before now (log) | now -->'},
            'showlegend' : False,
        }
    config = {
            'staticPlot' : True,
            }
    min_y = 0
    max_y = 1
    for i,s in enumerate(*args):
        try:
            name, index = s.split('__')
            index = int(index)
            assert name in names
        except:
            continue
        cfg_doc = base.db.GetSensorSettings(name)
        if index >= len(cfg_doc['readings']):
            continue
        description = cfg_doc['readings'][index]['description']
        points = np.array(base.db.GetData(name=name, index=index, start_time=start_time),
                          dtype=[('ts', np.int64), ('v', np.float32)])
        print('Got %i points for %s' % (len(points), s))
        if not len(points):
            continue
        points['ts'] = points['ts'][-1] - points['ts'] + 1  # time before now
        if points['ts'][0] > decimate_after and len(points) > num_pts:  # decimate
            num_old_pts = np.count_nonzero(points['ts'] > decimate_after)
            num_new_pts = len(points) - num_old_pts
            if num_new_pts > num_pts:  # not likely but possible
                points = points[points['ts'] < decimate_after]
            else:
                rows_to_keep = np.arange(num_new_pts)
                rows_to_keep = np.append(rows_to_keep,
                        num_new_pts + np.linspace(start=0,
                                                  stop=num_old_pts,
                                                  num=num_pts-num_new_pts,
                                                  endpoint=False,
                                                  dtype=np.int32))
                points = points[len(points) - rows_to_keep - 1]

        print(points['ts'][0])
        print(points['ts'][-1])
        earliest_t = max(earliest_t, points['ts'][0])
        data.append({
            'mode' : 'lines',
            'x' : list(map(int, points['ts'])),  # have to uncast from numpy types
            'y' : list(map(float, points['v'])),  # so json encoding works
            'line' : {'color' : colors[i%3], 'width' : 1}
            })
        if i == 0:
            key = 'yaxis'
            min_y = float(points['v'].min())
            max_y = float(points['v'].max())
        else:
            key = 'yaxis%i' % (i+1)
        layout[key] = {
            'title' : description,
            'titlefont' : {'color' : colors[i%3]},
            'tickfont' : {'color' : colors[i%3]},
            }
        if i > 0:
            data[-1]['yaxis'] = 'y%i' % (i+1)
    layout['xaxis']['range'] = [np.log10(earliest_t), 1]
    if len(data) > 1:
        layout['grid'] = {'pattern' : 'coupled',
                          'rows' : len(data),
                }
    for l,t in zip(['minute','hour','day','week'],[60,3600,86400,86400*7]):
        if t > earliest_t:
            break
        data.append({
            'mode' : 'line',
            'x' : [t,t],
            'y' : [min_y, max_y],
            'line' : {'dash' : 'dot', 'width' : 3, 'color' : 'rgb(192,192,192)'}
            })

    return JsonResponse({'data' : data, 'layout' : layout, 'config' : config})

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
            #if 'Test' in key:
            #    print(tabs[key])
            tabs[key] = tabs[key][:-4]
    return JsonResponse(tabs)
