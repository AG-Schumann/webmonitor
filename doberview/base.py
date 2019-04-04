from Doberman import DobermanDB

db = DobermanDB.DobermanDB(appname='webmonitor')

_error_codes = {
        '00' : 'No error',
        '01' : 'Invalid alarm values'
        }

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

def detail_context(name, error_code, **kwargs):
    context = base_context(**kwargs)
    sensor_doc = db.GetSensorSettings(name)
    del sensor_doc['heartbeat']
    del sensor_doc['_id']
    readings = {}
    for rd_name in sensor_doc['readings']:
        readings[rd_name] = db.GetReading(name, rd_name)['description']
    context.update({'sensordoc' : sensor_doc, 'readings' : readings,
        'baudrates' : [9600,19200,38400,57600]})
    if error_code is not None:
        context.update({'error_msg' : _error_codes[error_code]})

    return context

def index_context(**kwargs):
    context = base_context(**kwargs)

    return context

