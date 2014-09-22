import datetime

from story.analytics import count_rss
from story.models import Story, HourCount, HourCountSource, Source
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = 'Gets hour data once an hour'

	def add_arguments(self, parser):
		bob = 5

	def handle(self, *args, **options):
		t = datetime.datetime.now()
		for story in Story.objects.all():
			hc = HourCount(story=story, date=t)
			hc.save()
			for source in Source.objects.all():
				hcs = HourCountSource(hour_count=hc, source=source, count=0)
				hcs.save()
				count_rss(hcs)
