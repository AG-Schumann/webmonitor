from django.urls import path, re_path

from . import views

urlpatterns = [
        path('', views.index, name='index'),
        path('getoverview', views.getoverview, name='getoverview'),
        path('getalarms', views.getalarms, name='getalarms'),
        path('getlogs', views.getlogs, name='getlogs'),
        re_path(r'^detail/(?P<name>[^/]+)/$', views.detail, name='detail'),
        re_path(r'^getdata/(?P<name>[^/]+)/(?P<data_index>[0-9]+)/(?P<sincewhen>(?:[0-9]{1,4})(?:hr|day|wk|mo))/$', views.getdata, name='getdata'),
        ]
