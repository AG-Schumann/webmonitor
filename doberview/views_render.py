from django.shortcuts import render

from . import base

def detail(request, name, error_code=None):
    if name not in base.db.Distinct('settings','sensors','name'):
        return index(request)
    context = base.detail_context(name, error_code)
    return render(request, 'doberview/detail.html', context)

def index(request):
    context = base.index_context()
    return render(request, 'doberview/index.html', context)

def trend(request):
    sensor_names = base.db.Distinct('settings','sensors','name')
    context = base.trend_context()
    return render(request, 'doberview/trend.html', context)

