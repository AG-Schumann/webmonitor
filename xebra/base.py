from pymongo import MongoClient
from Doberman import Database
import os

client = MongoClient(os.environ['DOBERMAN_MONGO_URI'])
db = Database(client, experiment_name='xebra')

_error_codes = {
    '00': 'No error',
    '01': 'Invalid alarm values'
}


def client(meta):
    return {'client_addr': meta['REMOTE_ADDR'] if 'REMOTE_ADDR' in meta else 'web',
            'client_name': meta['REMOTE_HOST'] if 'REMOTE_HOST' in meta else 'web',
            'client_user': meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}


def is_schumann_subnet(meta):
    ip = client(meta)['client_addr']
    subnet, _ = ip.rsplit('.', maxsplit=1)
    return subnet == '10.4.73'


def base_context(**kwargs):
    context = {}
    context.update(kwargs)
    sensor_names = sorted(db.distinct('settings', 'sensors', 'name'))
    context['sensors'] = sensor_names

    return context


def pmt_context(**kwargs):
    context = base_context(**kwargs)
    context['pmt_crate_channels'] = list(range(12))

    return context


def hosts_context(**kwargs):
    context = base_context(**kwargs)
    host_names = sorted(db.distinct('common', 'hosts', 'hostname'))
    context['hosts'] = host_names

    return context


def detail_context(error_code, **kwargs):
    context = base_context(**kwargs)
    if error_code is not None:
        context.update({'error_msg': _error_codes[error_code]})
    context['types'] = ['pid', 'time_since', 'simple']
    return context


def alarms_context(**kwargs):
    context = base_context(**kwargs)
    context['aggregations'] = sorted(db.distinct('settings', 'alarm_aggregations', 'name'))
    context['types'] = ['pid', 'time_since', 'simple']
    return context


def index_context(**kwargs):
    context = base_context(**kwargs)
    host_names = sorted(db.distinct('common', 'hosts', 'hostname'))
    context['hosts'] = host_names

    return context


def contact_context(**kwargs):
    context = base_context(**kwargs)
    contacts = []
    for contact in db.read_from_database('settings', 'contacts'):
        if contact['name'] in ['MarcS', 'SebastianL']:
            continue
        contacts.append({'name': contact['name'], 'status': contact['status']})
    context.update({'contacts': contacts})

    return context
