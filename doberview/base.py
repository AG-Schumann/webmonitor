from pymongo import MongoClient
from Doberman import DobermanDB

#with open('/home/darryl/Work/doberman/connection_uri','r') as f:
#    client = MongoClient(f.read().strip())
#    db = Database(client, appname='webmonitor')
#    db.experiment_name = 'xebra'
db = DobermanDB.DobermanDB(appname='webmonitor')

_error_codes = {
        '00' : 'No error',
        '01' : 'Invalid alarm values'
        }

def client(meta):
    return {'client_addr' : meta['REMOTE_ADDR'] if 'REMOTE_ADDR' in meta else 'web',
            'client_name' : meta['REMOTE_HOST'] if 'REMOTE_HOST' in meta else 'web',
            'client_user' : meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}

def is_schumann_subnet(meta):
    ip = client(meta)['client_addr']
    subnet, _ = ip.rsplit('.', maxsplit=1)
    return subnet=='10.4.73'

def base_context(**kwargs):
    context = {}
    context.update(kwargs)
    sensor_names = sorted(db.Distinct('settings','sensors','name'))
    context['sensors'] = sensor_names
    for to_remove in db.readFromDatabase('settings','webhooks',{},onlyone=True)['sensors_to_hide']:
        try:
            context['sensors'].remove(to_remove)
        except:
            pass

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

def contact_context(**kwargs):
    context = base_context(**kwargs)
    contacts = []
    for contact in db.readFromDatabase('settings','contacts'):
        if contact['name'] in ['MarcS','SebastianL']:
            continue
        contacts.append({'name' : contact['name'], 'status' : contact['status']})
    context.update({'contacts' : contacts})

    return context
