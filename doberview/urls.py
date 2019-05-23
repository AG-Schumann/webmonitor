from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from django_pam.accounts.views import LoginView, LogoutView

from . import views_render
from . import views_post
from . import views_get

urlpatterns = [
        path('',
             views_render.index,
             name='index'),

        path('getoverview',
             views_get.getoverview,
             name='getoverview'),

        path('getalarms',
             views_get.getalarms,
             name='getalarms'),

        path('getlogs',
             views_get.getlogs,
             name='getlogs'),

        re_path(r'^detail/(?:(?P<error_code>[^/]+)/)?$',
                views_render.detail,
                name='detail'),

        re_path(r'^getreadings/(?P<name>[^/]+)/$',
                views_get.getreadings,
                name='getreadings'),

        re_path('r^getdata/(?:([^/]+)/)+$',
                views_get.getdata,
                name='getdata'),

        path('trend',
             views_render.trend,
             name='trend'),

        re_path(r'^startstop/$',
                views_post.startstop,
                name='startstop'),

        re_path(r'^change_address/$',
                views_post.change_address,
                name='change_address'),

        re_path(r'^log_command/$',
                views_post.log_command,
                name='log_command'),

        re_path(r'get_sensor_details/(?P<sensor_name>[^/]+)/$',
                views_get.get_sensor_details,
                name='get_sensor_details'),

        re_path(r'get_reading_detail/(?P<sensor_name>[^/]+)/(?P<reading_name>[^/]+)/$',
                views_get.get_reading_detail,
                name='get_reading_detail'),

        re_path(r'^change_reading/$',
                views_post.change_reading,
                name='change_reading'),

        re_path(r'^/account/login/$', views_render.login, name='log_in'),
        re_path(r'^/account/logout/$', views_render.logout, name='log_out'),

        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
