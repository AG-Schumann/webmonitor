from django.shortcuts import render

from . import base

def detail(request, error_code=None):
    context = base.detail_context(error_code)
    return render(request, 'pancake/detail.html', context)

def index(request):
    context = base.index_context()
    return render(request, 'pancake/index.html', context)

def pmts(request):
    context = base.pmt_context()
    return render(request, 'pancake/caen_hv.html', context)

def contacts(request):
    context = base.contact_context()
    return render(request, 'pancake/contacts.html', context)

def diagrams(request):
    return render(request, 'pancake/diagrams.html')

def hosts(request):
    context = base.hosts_context()
    return render(request, 'pancake/hosts.html', context)
