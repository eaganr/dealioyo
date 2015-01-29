from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from story.models import Story, Keyword, Headline, HeadlineLink, HourCount, StoryLink

def home(request):
	context = {}
	return render(request, 'dealio/home.html', context)
