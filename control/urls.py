from django.urls import path, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views_render, views_post, views_get

urlpatterns = [
        re_path(r'^runs/(?:(?P<msgcode>(?:err|msg)_[a-z]+)/)?$',
            views_render.runs, name='runs'),

        path("runs_todo/",
            views_render.runs_todo, name='runs_todo'),

        re_path(r'^config/(?:(?P<msgcode>[^/]+)/)?$',
            views_render.config, name='config'),

        re_path(r'^(?:(?P<msgcode>[^/]+)/)?$',
            views_render.main, name='main'),

        path('start', views_post.start, name='start'),
        path('stop', views_post.stop, name='stop'),
        path('led', views_post.led, name='led'),
        path('pause_toggle', views_post.pause_toggle, name='pause_toggle'),

        re_path('^get_status$',
            views_get.get_status, name='get_status'),
        
        
        re_path('^get_runs/(?P<experiment>[^/]+)/(?:(?P<limit>[1-9])/)?$',
            views_get.get_runs, name='get_runs'),

        
        re_path('^get_status_history$',
            views_get.get_status_history, name='get_status_history'),

        re_path('^cfg/(?:(?P<act>[a-z]+)/)$',
            views_post.cfg, name="cfg"),

        re_path('^get_cfg_doc/(?P<name>[a-zA-Z0-9_\\-]+)/$',
            views_get.get_cfg_doc, name="get_cfg_doc"),

        re_path("^runs/get_run_detail/(?P<experiment>[^/]+)/(?P<runid>[1-9]*[0-9])/$",
            views_get.get_run_detail, name="get_run_detail"),

        re_path("^get_upcoming_runs/(?P<experiment>[^/]+)/$",
            views_get.get_upcoming_runs, name="get_upcoming_runs"),
        
        re_path("^clear_upcoming_runs/(?P<experiment>[^/]+)/$",
            views_get.clear_upcoming_runs, name="clear_upcoming_runs"),
        
        re_path("^clear_a_upcoming_run/(?P<experiment>[^/]+)/(?P<objectid>[^/]+)/$",
            views_get.clear_a_upcoming_run, name="clear_a_upcoming_run"),
        
        re_path("^list_upcoming_runs/(?P<experiment>[^/]+)/$",
            views_get.get_upcoming_runs_list, name="get_upcoming_runs_list"),
        
        path("runs/update_run/", views_post.update_run, name="update_run"),
]

urlpatterns += staticfiles_urlpatterns()
