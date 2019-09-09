from django.shortcuts import render

from . import base

def detail(request, error_code=None):
    context = base.detail_context(error_code)
    return render(request, 'doberview/detail.html', context)

def index(request):
    context = base.index_context()
    return render(request, 'doberview/index.html', context)

def pmts(request):
    context = base.trend_context()
    return render(request, 'doberview/caen_hv.html', context)

def contacts(request):
    context = base.contact_context()
    return render(request, 'doberview/contacts.html', context)
