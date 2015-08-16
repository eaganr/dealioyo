import datetime
import urllib2
from httplib import BadStatusLine
from cookielib import CookieJar
from bs4 import BeautifulSoup

from story.analytics import in_last_hour
from story.models import Story, HourCount, HourCountSource, Source, Keyword, StoryLink
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = 'Gets hour data once an hour'

	def add_arguments(self, parser):
		bob = 5

	def handle(self, *args, **options):
		t = datetime.datetime.now()
		hour_counts = {}
		for story in Story.objects.all():
			hc = HourCount(story=story, date=t)
			hc.save()
			hour_counts
			for source in Source.objects.all():
				hcs = HourCountSource(hour_count=hc, source=source, count=0)
				hcs.save()

		cj = CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		for source in Source.objects.all():
			rss = str(urllib2.urlopen(source.rss_url).read())

			soup = BeautifulSoup(rss)
			for item in soup.find_all("item"):
				#check date is in last hour
				date_text = item.find("pubdate").text
				
				if date_text[-3:] != "GMT":
					date_text =  date_text[:-3] + " GMT"
				

				the_time = datetime.datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %Z")
				the_time = the_time + datetime.timedelta(hours=source.hour_offset)

				last24 = start_time = datetime.datetime.now() + datetime.timedelta(hours=-24)
				if in_last_hour(the_time):
					link = item.find("link").text
					title = item.find("title").text
					if len(StoryLink.objects.filter(date__gte=last24, url=link)) == 0 and len(StoryLink.objects.filter(url=link)) == 0:
						if len(StoryLink.objects.filter(date__gte=last24, title=title)) == 0:
							try:
								html = str(opener.open(link).read()).lower().decode('utf-8')
							except BadStatusLine:
								html = ""
							except UnicodeDecodeError:
								html = ""
							if source.start_text in html:
								html = html.split(source.start_text, 1)[1]
							if source.end_text in html:
								html = html.split(source.end_text, 1)[0]
							if html != "":
								for story in Story.objects.all():
									for kw in Keyword.objects.filter(story=story):
										kwFound = False
										if " " + kw.keyword in item.find("description").text or kw.keyword + " " in item.find("description").text:
											kwFound = True
										if " " + kw.keyword in item.find("title").text or kw.keyword + " " in item.find("title").text:
											kwFound = True
										
										if kwFound:
											hcs = HourCountSource.objects.filter(source=source,
																			  	 hour_count__story=kw.story,
																			  	 hour_count__date=t)[0]
											hcs.count += 1
											hcs.save()
											# add as StoryLink
											sl = StoryLink(url=link,
														   date=the_time,
														   title=item.find("title").text,
														   hour_count_source=hcs)
											sl.save()
											break
					else:
						#if not on last hour then go to next source
						break
