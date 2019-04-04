from Doberman import DobermanDB

db = DobermanDB.DobermanDB(appname='webmonitor')

def base_context(**kwargs):
    context = {}
    context.update(kwargs)
    sensor_names = sorted(db.Distinct('settings','sensors','name'))
    #sensor_names.remove('TestSensor')
    context['sensors'] = sensor_names

    return context

def trend_context(**kwargs):
    context = base_context(**kwargs)

    return context

def detail_context(name, **kwargs):
    context = base_context(**kwargs)
    sensor_doc = db.GetSensorSettings(name)
    del sensor_doc['heartbeat']
    del sensor_doc['_id']
    readings = {}
    for rd_name in sensor_doc['readings']:
        readings[rd_name] = db.GetReading(name, rd_name)['description']
    context.update({'sensordoc' : sensor_doc, 'readings' : readings,})

    return context

def index_context(**kwargs):
    context = base_context(**kwargs)

    return context

