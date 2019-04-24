from django.shortcuts import render

from . import base

def detail(request, error_code=None):
    context = base.detail_context(error_code)
    return render(request, 'doberview/detail.html', context)

def index(request):
    context = base.index_context()
    return render(request, 'doberview/index.html', context)

def trend(request):
    sensor_names = base.db.Distinct('settings','sensors','name')
    context = base.trend_context()
    return render(request, 'doberview/trend.html', context)

def login(request):
    context = base.base_context()

    return render(request, 'doberview/login.html', context)

def logout(request):
    context = base.base_context()

    return render(request, 'doberview/logout.html', context)
