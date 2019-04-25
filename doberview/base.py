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
    sensor_names.remove('TestSensor')
    sensor_names.remove('baris_test')
    context['sensors'] = sensor_names

    return context

def trend_context(**kwargs):
    context = base_context(**kwargs)

    return context

def detail_context(error_code, **kwargs):
    context = base_context(**kwargs)
    if error_code is not None:
        context.update({'error_msg' : _error_codes[error_code]})

    return context

def index_context(**kwargs):
    context = base_context(**kwargs)

    return context

