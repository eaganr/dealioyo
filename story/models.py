from django.db import models

import datetime

# Create your models here.

class Story(models.Model):
	title = models.CharField(max_length=100)
	description = models.CharField(max_length=5000)
	start_date = models.DateTimeField(blank=True,null=True)
	slug = models.CharField(max_length=50)

	def headlines(self):
		return Headline.objects.filter(story=self)

	def keywords(self):
		return Keyword.objects.filter(story=self)

	def todays_links(self):
		start_time = datetime.datetime.now() + datetime.timedelta(hours=-24)
		story_links = StoryLink.objects.filter(hour_count_source__hour_count__story=self, date__gt=start_time)
		return story_links

	def todays_links_urls(self):
		story_links = self.todays_links()
		urls = []
		for sl in story_links:
			urls.append(sl.url)
		return urls


class Keyword(models.Model):
	story = models.ForeignKey('Story')
	keyword = models.CharField(max_length=50)


class Headline(models.Model):
	story = models.ForeignKey('Story')
	date = models.DateTimeField(blank=True,null=True)
	title = models.CharField(max_length=100)
	description = models.CharField(max_length=2000)

	def links(self):
		return HeadlineLink.objects.filter(headline=self)


class StoryLink(models.Model):
	title = models.CharField(max_length=200)
	url = models.CharField(max_length=400)
	hour_count_source = models.ForeignKey('HourCountSource')
	date = models.DateTimeField(blank=True,null=True)


class HeadlineLink(StoryLink):
	headline = models.ForeignKey('Headline')
	

class Source(models.Model):
	name = models.CharField(max_length=100)
	homepage = models.CharField(max_length=100)
	rss_url = models.CharField(max_length=200)
	start_text = models.CharField(max_length=50)
	end_text = models.CharField(max_length=50)
	hour_offset = models.IntegerField() #offset from GMT

# saves Story object Keyword mentions in last hour
class HourCount(models.Model):
	story = models.ForeignKey('Story')
	date = models.DateTimeField(blank=True,null=True)

	def hour_count_sources(self):
		return HourCountSource.objects.filter(hour_count=self)

	def count(self):
		total = 0
		for hcs in HourCountSource.objects.filter(hour_count=self):
			total += hcs.count
		return total


class HourCountSource(models.Model):
	hour_count = models.ForeignKey('HourCount')
	source = models.ForeignKey('Source')
	count = models.IntegerField()
