import datetime
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from story.models import Story, Keyword, Headline, HeadlineLink, HourCount, StoryLink

# Create your views here.

def story(request, slug):
	context = {}
	if len(Story.objects.filter(slug=slug)):
		context["story"] = Story.objects.get(slug=slug)
	else:
		context["error"] = "Not Found"

	return render(request, 'story/story.html', context)

def story_chart(request, slug):
	context = {}
	if len(Story.objects.filter(slug=slug)):
		context["story"] = Story.objects.get(slug=slug)
		start_time = datetime.datetime.now() + datetime.timedelta(hours=-24)
		start_time = start_time.replace(minute=0, second=0)
		hours = HourCount.objects.filter(story=context["story"], date__gte=start_time)
		hours_reference = [0]*24
		for hour in hours:
			hours_reference[(hour.date.hour-start_time.hour-1)%24] = hour
		context["hours"] = hours_reference
	else:
		context["error"] = "Not Found"

	return render(request, 'story/story_chart.html', context)

def headline(request, slug, headline):
	context = {}
	return LineChartJSONView.as_view()
	if len(Story.objects.filter(slug=slug)):
		story = Story.objects.get(slug=slug)
		context["story"] = story
		if len(Headline.objects.filter(pk=headline, story=story)):
			context["headline"] = Headline.objects.get(pk=headline, story=story)
	else:
		context["error"] = "Not Found"

	return render(request, 'story/headline.html', context)


def line_json(request):
	story = None
	mode = ""
	if request.method == "GET":
		if "story" in request.GET:
			story = Story.objects.get(pk=request.GET["story"])
		if "mode" in request.GET:
			mode = request.GET["mode"]

	labels = []
	datasets = {"pointColor": "rgba(203, 202, 198, 1)",
				"strokeColor": "rgba(203, 202, 198, 1)",
				"fillColor": "rgba(203, 202, 198, 0.5)",
				"pointStrokeColor": "#fff"}
	if mode == "day":
		#labels
		current_hour = datetime.datetime.now().hour
		for hour in range(0	,24):
			if (current_hour+hour)%24 <= 12:
				labels.append(str((current_hour+hour)%24) + " am")
			else:
				labels.append(str((current_hour+hour)%24-12) + " pm")	
		#data
		data = [0]*24
		start_time = datetime.datetime.now() + datetime.timedelta(hours=-24)
		start_time = start_time.replace(minute=0, second=0)
		hours = HourCount.objects.filter(story=story, date__gte=start_time)
		for hour in hours:
			data[(hour.date.hour-start_time.hour-1)%24] = hour.count()
		datasets["data"] = data
	info = {"labels": labels, "datasets": [datasets]}
	return HttpResponse(json.dumps(info), content_type="application/json")