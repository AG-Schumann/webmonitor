from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, JsonResponse

import datetime
from pymongo import MongoClient
import os
import re


def overviewdocs():
    """
    Returns the html-formatted rows for the status table
    """
    client = MongoClient(os.environ['MONITOR_URI'])
    rows = {}

    docrow_base = '<tr><td rowspan={nval}>{name}</td><td rowspan={nval}>{runmode}</td><td rowspan={nval} style="color:{color}">{status}</td><td rowspan={nval}>{when}</td>'
    value_base = "<td>" + "</td><td>".join(['{warn_low}','{value}','{warn_high}','{desc}','{stat}']) + '</td>'

    for doc in client['settings']['controllers'].find({}):
        name = doc['name']
        nval = int(doc['number_of_data'])
        descs = doc['description']
        runmode = doc['runmode']
        alarm_status = doc['alarm_status'][runmode]
        if doc['online']:
            if doc['status'][runmode] != 'ON':
                status = 'sleep'
                color = '#FF7F00'
            else:
                status = 'online'
                color = '#00DD00'
        else:
            status = 'offline'
            color = '#DD0000'

        if status == 'online':
            warns_low = doc['warning_low'][runmode]
            warns_high = doc['warning_high'][runmode]
            for row in client['data'][name].find({},sort=[('when',-1)],limit=1):
                when = row['when'].strftime("%Y-%m-%d %H:%M:%S")
                try:
                    values = list(map('{:.2f}'.format, row['data']))
                except ValueError:
                    values = ['-']*nval
                stats = row['status']
        else:
            warns_low = ['-']*nval
            warns_high = ['-']*nval
            stats = ['-']*nval
            when = '-'
            values = ['-']*nval

        docrow = docrow_base.format(nval=nval,name=name,runmode=runmode,
                color=color,when=when,status=status)
        for i in range(nval):
            al=alarm_status[i]
            value_chunk = value_base.format(warn_low=warns_low[i] if al=='ON' else '-',
                    value=values[i], warn_high=warns_high[i] if al=='ON' else '-',
                    desc=descs[i], stat=stats[i])
            if i:
                rows['%s_row_%i' % (name, i)] = '<tr>' + value_chunk + '</tr>'
            else:
                rows['%s_row_%i' % (name, i)] = docrow + value_chunk + '</tr>'
    client.close()
    return rows

def getalarms(request):
    if request.method != 'GET':
        pass
    client = MongoClient(os.environ['MONITOR_URI'])
    docs = []
    for row in client['logging']['alarm_history'].find({},sort=[('when',-1)],limit=10):
        docs.append({
            'when' : row['when'].strftime("%Y-%m-%d %H:%M:%S"),
            'name' : row['name'],
            'message' : row['msg'],
            })
    client.close()
    return JsonResponse(docs, safe=False)

def getlogs(request):
    if request.method != 'GET':
        pass
    client = MongoClient(os.environ['MONITOR_URI'])
    docs = []
    levels = {
            10 : 'debug',
            20 : 'info',
            30 : 'warning',
            40 : 'error',
            50 : 'critical',
        }
    for row in client['logging']['logs'].find({},sort=[('when',-1)],limit=10):
        docs.append({
            'when' : row['when'].strftime("%Y-%m-%d %H:%M:%S"),
            'level' : levels[int(row['level'])],
            'name' : row['name'],
            'message' : row['msg'],
        })
    client.close()
    return JsonResponse(docs, safe=False)

def getoverview(request):
    return JsonResponse(overviewdocs())

def index(request):
    client = MongoClient(os.environ['MONITOR_URI'])
    docs = {}
    for row in client['settings']['controllers'].find({}).sort([('name', 1)]):
        docs[row['name']] = list(range(int(row['number_of_data'])))
    client.close()
    return render(request, 'doberview/index.html', {'controller_list': docs})

def detail(request, name):
    client = MongoClient(os.environ['MONITOR_URI'])
    fulldoc = client['settings']['controllers'].find_one({'name' : name})
    fields = ['name','status','alarm_status','warning_low','warning_high','alarm_low','alarm_high',
            'description','additional_params','runmode','online']
    doc = {f : fulldoc[f] for f in fields}
    names = client['settings']['controllers'].distinct('name')
    client.close()
    return render(request, 'doberview/detail.html', {'detaildoc': doc, 'controller_list' : names})

def getdata(request, name, data_index, sincewhen):
    client = MongoClient(os.environ['MONITOR_URI'])
    x = []
    y = []
    time_end = datetime.datetime.now()
    pattern = r'(?P<value>[0-9]+)(?P<which>hr|day|wk|mo)'
    m = re.search(pattern, sincewhen)
    if not m:
        print('Match failed!')
        seconds = 86400  # default 1 day
    else:
        conv_dict = {'hr' : 3600,
                     'day' : 86400,
                     'wk' : 7*86400,
                     'mo' : 28*86400,
                     }
        seconds = int(m.group('value'))*conv_dict[m.group('which')]
    time_start = time_end - datetime.timedelta(seconds=seconds)

    query = {'$gte' : {'when' : time_start}, '$lte' : {'when' : time_end}}
    for doc in client['data'][name].find(query):
        x.append(doc['when'].timestamp()*1000)  # JS uses milliseconds
        y.append(doc['data'][data_i])
    configdoc = client['settings']['controllers'].find_one({'name' : name})
    desc = configdoc['description'][data_index]
    runmode = configdoc['runmode']
    levels = {'warn_low' : configdoc['warning_low'][runmode][data_index],
              'warn_high' : configdoc['warning_high'][runmode][data_index],
              'alarm_low' : configdoc['alarm_low'][runmode][data_index],
              'alarm_high' : configdoc['alarm_high'][runmode][data_index]}
    client.close()
    return JsonResponse({'x' : x, 'y' : y, 'levels' : levels, 'desc' : desc})

def plotter(request):
    pass
