from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
        path('', views.status, name='status'),
        path('start', views.start, name='start'),
        path('stop', views.stop, name='stop'),
        path('arm', views.arm, name='arm'),
        path('disarm', views.disarm, name='disarm'),
        path('get_status', views.get_status, name='get_status'),
        path('get_runs', views.get_runs, name='get_runs'),
        re_path('^get_status_history/(?P<limit>[1-9][0-9]*)?$', views.get_status_history, name='get_status_history'),
]

urlpatterns += staticfiles_urlpatterns()
