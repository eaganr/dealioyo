from django.shortcuts import render
from story.models import Story, Keyword, Headline, HeadlineLink

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
