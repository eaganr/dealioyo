import datetime

from django.shortcuts import render
from story.models import Story, Keyword, Headline, HeadlineLink, HourCount

# Create your views here.

def story(request, slug):
	context = {}
	if len(Story.objects.filter(slug=slug)):
		context["story"] = Story.objects.get(slug=slug)
	else:
		context["error"] = "Not Found"

	return render(request, 'story/story.html', context)


def headline(request, slug, headline):
	context = {}
	if len(Story.objects.filter(slug=slug)):
		story = Story.objects.get(slug=slug)
		context["story"] = story
		if len(Headline.objects.filter(pk=headline, story=story)):
			context["headline"] = Headline.objects.get(pk=headline, story=story)
	else:
		context["error"] = "Not Found"

	return render(request, 'story/headline.html', context)

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

import pdb;
class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
    	current_hour = datetime.datetime.now().hour
    	labels = []
    	for hour in range(0,24):
    		if (current_hour+hour)%24 <= 12:
    			labels.append(str((current_hour+hour)%24) + " am")
    		else:
    			labels.append(str((current_hour+hour)%24-12) + " pm")
    	print labels
        return labels

    def get_data(self):
    	data = []
    	for story in Story.objects.all():
    		sub_data = [0]*24
    		start_time = datetime.datetime.now() + datetime.timedelta(hours=-24)
    		start_time = start_time.replace(minute=0, second=0)
    		hours = HourCount.objects.filter(story=story, date__gte=start_time)
    		for hour in hours:
    			sub_data[(hour.date.hour-start_time.hour-1)%24] = hour.count()
    		data.append(sub_data)
		return data


line_chart = TemplateView.as_view()
line_chart_json = LineChartJSONView.as_view()