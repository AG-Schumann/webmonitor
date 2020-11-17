from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views_render
from . import views_post
from . import views_get

urlpatterns = [

                  path('',
                       views_render.index,
                       name='index'),

                  path('error',
                       views_render.error,
                       name='error'),

                  path('getoverview',
                       views_get.get_overview,
                       name='getoverview'),

                  path('getalarms',
                       views_get.get_alarms,
                       name='getalarms'),

                  path('getlogs',
                       views_get.get_logs,
                       name='getlogs'),

                  re_path(r'^detail/(?:(?P<error_code>[^/]+)/)?$',
                          views_render.detail,
                          name='detail'),
                  path('alarms',
                       views_render.alarms,
                       name='alarms'),
                  #        re_path(r'^getreadings/(?P<name>[^/]+)/$',
                  #                views_get.getreadings,
                  #                name='getreadings'),

                  re_path(
                      r'^get_shifts/(?P<start>20(?:19|2[0-9])-(?:0[1-9]|1[012])-(?:[012][0-9]|3[01]))/(?P<end>20('
                      r'?:19|2[0-9])-(?:0[1-9]|1[012])-(?:[012][0-9]|3[01]))/$',
                      views_get.get_shifts,
                      name='get_shifts'),

                  re_path(
                      r'^get_shift_detail/(?P<date>(?:2019|202[0-9])-(?:0[1-9]|1[012])-(?:0[1-9]|[12][0-9]|3[01]))/$',
                      views_get.get_shift_detail,
                      name='get_shift_detail'),

                  path('caen_hv',
                       views_render.pmts,
                       name='caen_hv'),

                  re_path(r'^change_address/$',
                          views_post.change_address,
                          name='change_address'),

                  re_path(r'^log_command/$',
                          views_post.log_command,
                          name='log_command'),

                  re_path(r'get_sensor_details/(?P<sensor_name>[^/]+)/$',
                          views_get.get_sensor_details,
                          name='get_sensor_details'),

                  re_path(r'get_host_detail/(?P<host_name>[^/]+)/$',
                          views_get.get_host_detail,
                          name='get_host_detail'),

                  re_path(r'get_reading_detail/(?P<sensor_name>[^/]+)/(?P<reading_name>[^/]+)/$',
                          views_get.get_reading_detail,
                          name='get_reading_detail'),

                  re_path(r'get_alarm_aggregation/(?P<name>[^/]+)/$',
                          views_get.get_alarm_aggregation,
                          name='get_alarm_aggregation'),

                  re_path(r'change_reading/$',
                          views_post.change_reading,
                          name='change_reading'),

                  re_path(r'^change_default/$',
                          views_post.change_default,
                          name='change_default'),

                  re_path(r'^change_aggregation/$',
                          views_post.change_aggregation,
                          name='change_aggregation'),
                  path('contacts',
                       views_render.contacts,
                       name='contacts'),

                  path('diagrams',
                       views_render.diagrams,
                       name='diagrams'),

                  path('hosts',
                       views_render.hosts,
                       name='hosts'),

                  re_path(r'update_shift/$',
                          views_post.update_shift,
                          name='update_shift'),

                  re_path(r'add_new_contact/$',
                          views_post.add_new_contact,
                          name='add_new_contact'),

                  re_path(r'^get_pmts/(?P<speed>fast|slow)/$',
                          views_get.get_pmts,
                          name='get_pmts'),

                  re_path(r'^update_pmts/$',
                          views_post.update_pmts,
                          name='update_pmts'),

                  re_path(r'scram/$',
                          views_post.scram,
                          name='scram'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
