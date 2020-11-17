from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonReponse
from pymongo import MongoClient
import os


def get_config_doc(request, mode):
    client = MongoClient(os.environ['MONITOR_URI'])
    coll = client['kodiaq']['config']
    doc = coll.find_one({'mode' : mode})
    client.close()
    return JsonResponse(doc)

def overview(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    client.close()
    return

#def update_mode_doc(request):
#    client = MongoClient(os.environ['MONITOR_URI'])
#    newdoc = request.POST[
