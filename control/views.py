from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from pymongo import MongoClient
import time
import datetime
import os

def client(meta):
    return {'client_addr' : meta['REMOTE_ADDR'],
            'client_name' : meta['REMOTE_HOST'],
            'client_user' : meta['REMOTE_USER'] if 'REMOTE_USER' in meta else 'web'}

def get_status(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    doc = client['kodiaq']['status'].find_one()
    del doc['_id']
    for k in ['mode','name','number']:
        if k not in doc:
            doc[k] = 'none'
    return JsonResponse(doc)



