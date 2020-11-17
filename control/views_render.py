from django.shortcuts import render

from . import base


def main(request, msgcode=None):
    context = base.base_context(msgcode=msgcode)

    return render(request, 'control/main.html', context)


def config(request, msgcode=None):
    context = base.config_context(msgcode=msgcode)

    return render(request, 'control/config.html', context)


def runs(request, msgcode=None):
    context = base.runs_context()
    return render(request, 'control/runs.html', context)


def runs_todo(request, msgcode=None):
    context = base.runs_context()
    return render(request, 'control/runs_todo.html', context)
