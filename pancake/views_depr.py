from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse

import datetime
from Doberman import DobermanDB
import os
import numpy as np
import json

from . import base


db = DobermanDB.DobermanDB()

def get_base_context():
    """
    Returns a dictionary with the necessary values for base.html
    """
    sensor_names = db.Distinct('settings','sensors','name')
    sensor_names.remove('TestSensor')

    return {'sensors' : sensor_names}

def overviewdocs():
    """
    Returns the html-formatted rows for the status table
    """
    client = MongoClient(os.environ['MONITOR_URI'])
    rows = {}

    docrow_base = '<tr><td rowspan={nval}>{name}</td><td rowspan={nval}>{runmode}</td><td rowspan={nval} style="color:{color}">{status}</td><td rowspan={nval}>{when}</td>'
    value_base = "<td>" + "</td><td>".join(['{warn_low}','{value}','{warn_high}','{desc}','{stat}']) + '</td>'

    for doc in client['settings']['sensors'].find({'name' : {'$nin' : ['TestSensor']}}):
        name = doc['name']
        nval = len(doc['readings'])
        runmode = doc['runmode']
        status = doc['status']
        colors = {
                'sleep' : '#FF7F00',
                'online' : '#00DD00',
                'offline' : '#DD0000'
        }
        if status == 'online':
            for row in client['data'][name].find({},sort=[('when',-1)],limit=1):
                when = row['when'].strftime("%Y-%m-%d %H:%M:%S")
                try:
                    values = list(map('{:.3g}'.format, row['data']))
                except (ValueError, TypeError):
                    values = ['-']*nval
                stats = row['status']
        else:
            stats = ['-']*nval
            when = '-'
            values = ['-']*nval

        docrow = docrow_base.format(nval=nval,name=name,runmode=runmode,
                color=colors[status],when=when,status=status)
        for i,reading in enumerate(doc['readings']):
            al=reading['level'][runmode]
            value_chunk = value_base.format(warn_low=reading['alarms'][al][0] if al>=0 else '-',
                    value=values[i], warn_high=reading['alarms'][al][1] if al>=0 else '-',
                    desc=reading['description'], stat=stats[i])
            if i:
                rows['%s_row_%i' % (name, i)] = '<tr>' + value_chunk + '</tr>'
            else:
                rows['%s_row_%i' % (name, i)] = docrow + value_chunk + '</tr>'
    doberdoc = client['settings']['defaults'].find_one()
    heartbeat = doberdoc['heartbeat']
    runmode = doberdoc['runmode']
    rows['doberman'] = '<tr><td>Doberman</td><td>' + runmode + '</td>'
    if doberdoc['status'] in ['online','sleep']:
        stat = doberdoc['status']
        rows['doberman'] += '<td style="color:%s">%s</td><td>%s</td>' % (colors[stat], stat, heartbeat.strftime("%Y-%m-%d %H:%M:%S"))
        rows['doberman'] += '<td colspan=5> </td>'
    else:
        rows['doberman'] += '<td style="color:#DD0000">offline</td><td colspan=6> </td>'
    rows['doberman'] += '</tr>'
    client.close()
    return rows



