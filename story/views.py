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
		mode = "day"
		if request.method == "GET":
			if "mode" in request.GET:
				mode = request.GET["mode"]
		if mode == "day":
			start_time = datetime.datetime.now() + datetime.timedelta(hours=-23)
			start_time = start_time.replace(minute=0, second=0)
			hours = HourCount.objects.filter(story=context["story"], date__gte=start_time)
			links = [[] for x in xrange(24)] 
			for hour in hours:
				links[(hour.date.hour-start_time.hour-1)%24].append(hour)
			context["links"] = links
		if mode == "week":
			links = [[] for x in xrange(7)]
			start_time = datetime.datetime.now() + datetime.timedelta(days=-6)
			start_time = start_time.replace(hour=0, minute=0, second=0)
			hours = HourCount.objects.filter(story=context["story"], date__gte=start_time)
			for hour in hours:
				links[(hour.date.day-start_time.day)%7].append(hour)
			context["links"] = links
		if mode == "month":
			#labels
			the_date = None
			current_time = datetime.datetime.now()
			if current_time.month == 1:
				the_date = current_time.replace(year=current_time.year-1,month=12)
			else:
				the_date = current_time.replace(month=current_time.month-1)
			start_time = the_date.replace(hour=0, minute=0, second=0)
			end_date = current_time + datetime.timedelta(days=1)
			dates = []
			day_count = 0
			while the_date.day != end_date.day or the_date.month != end_date.month:
				day_count += 1
				dates.append(the_date)
				the_date = the_date + datetime.timedelta(days=1)
			#data
			links = [[] for x in xrange(len(dates))]
			hours = HourCount.objects.filter(story=context["story"], date__gte=start_time)
			for hour in hours:
				for i in xrange(0,len(dates)):
					if hour.date.day == dates[i].day and hour.date.month == dates[i].month:
						links[i].append(hour)
			context["links"] = links
		context["mode"] = mode
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
	mode = "day"
	size = "large"
	if request.method == "GET":
		if "story" in request.GET:
			story = Story.objects.get(pk=request.GET["story"])
		if "mode" in request.GET:
			mode = request.GET["mode"]
		if "size" in request.GET:
			size = request.GET["mode"]

	labels = []
	datasets = {"pointColor": "rgba(203, 202, 198, 1)",
				"strokeColor": "rgba(112, 205, 239, 1)",
				"fillColor": "rgba(203, 202, 198, 0.5)",
				"pointStrokeColor": "#fff"}
	current_time = datetime.datetime.now()
	if mode == "day":
		#labels
		current_hour = current_time.hour
		for hour in range(0	,24):
			if (current_hour+hour)%24 <= 12:
				labels.append(str((current_hour+hour)%24) + " am")
			else:
				labels.append(str((current_hour+hour)%24-12) + " pm")	
		#data
		data = [0]*24
		start_time = datetime.datetime.now() + datetime.timedelta(hours=-23)
		start_time = start_time.replace(minute=0, second=0)
		hours = HourCount.objects.filter(story=story, date__gte=start_time)
		for hour in hours:
			data[(hour.date.hour-start_time.hour-1)%24] += hour.count()
		datasets["data"] = data
	
	if mode == "week":
		#labels
		the_date = current_time + datetime.timedelta(days=-6)
		start_time = the_date.replace(hour=0, minute=0, second=0)
		end_date = current_time + datetime.timedelta(days=1)
		dates = []
		weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
		while the_date.day != end_date.day or the_date.month != end_date.month:
			labels.append(str(weekdays[the_date.weekday()]) + ", " + str(the_date.day))
			dates.append(the_date)
			the_date = the_date + datetime.timedelta(days=1)
		#data
		data = [0]*len(labels)
		hours = HourCount.objects.filter(story=story, date__gte=start_time)
		for hour in hours:
			for i in xrange(0,len(dates)):
				if hour.date.day == dates[i].day and hour.date.month == dates[i].month:
					data[i] += hour.count()
		datasets["data"] = data
	if mode == "month":
		#labels
		the_date = None
		if current_time.month == 1:
			the_date = current_time.replace(year=current_time.year-1,month=12)
		else:
			the_date = current_time.replace(month=current_time.month-1)
		start_time = the_date.replace(hour=0, minute=0, second=0)
		end_date = current_time + datetime.timedelta(days=1)
		dates = []
		while the_date.day != end_date.day or the_date.month != end_date.month:
			labels.append(the_date.strftime("%d %B"))
			dates.append(the_date)
			the_date = the_date + datetime.timedelta(days=1)
		#data
		data = [0]*len(labels)
		hours = HourCount.objects.filter(story=story, date__gte=start_time)
		for hour in hours:
			for i in xrange(0,len(dates)):
				if hour.date.day == dates[i].day and hour.date.month == dates[i].month:
					data[i] += hour.count()
		datasets["data"] = data


	info = {"labels": labels, "datasets": [datasets]}
	return HttpResponse(json.dumps(info), content_type="application/json")