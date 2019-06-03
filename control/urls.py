from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views_render, views_post, views_get

urlpatterns = [
        re_path(r'^runs/(?:(?P<msgcode>[^/]+)/)?$', views_render.runs, name='runs'),
        re_path(r'^config/(?:(?P<msgcode>[^/]+)/)?$', views_render.config, name='config'),
        re_path(r'^(?:(?P<msgcode>[^/]+)/)?$', views_render.main, name='main'),

        path('start', views_post.start, name='start'),
        path('stop', views_post.stop, name='stop'),
        path('arm', views_post.arm, name='arm'),
        path('led', views_post.led, name='led'),

        path('get_status', views_get.get_status, name='get_status'),
        re_path('get_runs/(?P<experiment>[^/]+)/(?:(?P<limit>[1-9])/)?$', views_get.get_runs, name='get_runs'),
        path('get_status_history', views_get.get_status_history, name='get_status_history'),
        re_path('cfg/(?:(?P<act>[^/]+)/)$', views_post.cfg, name="cfg"),
        re_path('get_cfg_doc/(?P<name>[a-zA-Z_]+)/$', views_get.get_cfg_doc, name="get_cfg_doc"),
]

urlpatterns += staticfiles_urlpatterns()
