from django.conf.urls import patterns, url

from story import views
from story.models import Story

urlpatterns = patterns('',
    url(r'^$', views.story_index, name='story_index'),
    url(r'^(?P<slug>\w+)/$', views.story, name='story'),
    url(r'^(?P<slug>\w+)/chart', views.story_chart, name='story_chart'),
    url(r'^(?P<slug>\w+)/links', views.story_links, name='story_links'),
    url(r'^(?P<slug>\w+)/(?P<headline>\d+)/$', views.headline, name='headline'),

    url(r'^line_chart/json', views.line_json, name='line_json'),
)
