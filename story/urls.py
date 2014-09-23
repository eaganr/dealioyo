from django.conf.urls import patterns, url

from story import views
from story.models import Story

urlpatterns = patterns('',
    url(r'^(?P<slug>\w+)/$', views.story, name='story'),
    url(r'^(?P<slug>\w+)/(?P<headline>\d+)/$', views.headline, name='headline'),
    url(r'^line_chart/json/$', views.line_chart_json, name='line_chart_json'),
)