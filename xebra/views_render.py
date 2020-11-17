from django.shortcuts import render

from . import base


def error(request):
    context = base.index_context()
    return render(request, 'xebra/error.html', context)


def detail(request, error_code=None):
    context = base.detail_context(error_code)
    return render(request, 'xebra/detail.html', context)


def alarms(request):
    context = base.alarms_context()
    return render(request, 'xebra/alarms.html', context)


def index(request):
    context = base.index_context()
    return render(request, 'xebra/index.html', context)


def pmts(request):
    context = base.pmt_context()
    return render(request, 'xebra/caen_hv.html', context)


def contacts(request):
    context = base.contact_context()
    return render(request, 'xebra/contacts.html', context)


def diagrams(request):
    return render(request, 'xebra/diagrams.html')


def hosts(request):
    context = base.hosts_context()
    return render(request, 'xebra/hosts.html', context)
