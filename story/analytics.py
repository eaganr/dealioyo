import urllib2
import time
import datetime

from twython import Twython
from bs4 import BeautifulSoup
from httplib import BadStatusLine
from cookielib import CookieJar

from story.models import Story, StoryLink, Source, HourCount, HourCountSource

#return articles mentioning story keywords
def count_rss(hour_count_source):
	cj = CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	rss = str(urllib2.urlopen(hour_count_source.source.rss_url).read())
	soup = BeautifulSoup(rss)
	count = 0
	for item in soup.find_all("item"):
		#check date is in last hour
		date_text = item.find("pubdate").text
		
		if date_text[-3:] != "GMT":
			date_text =  date_text[:-3] + " GMT"
		

		the_time = datetime.datetime.strptime(date_text, "%a, %d %b %Y %H:%M:%S %Z")
		the_time = the_time + datetime.timedelta(hours=hour_count_source.source.hour_offset)

		if in_last_hour(the_time):
			link = item.find("link").text
			if link not in hour_count_source.hour_count.story.todays_links_urls():
				try:
					html = str(opener.open(link).read()).lower().decode('utf-8')
				except BadStatusLine:
					html = ""
				except UnicodeDecodeError:
					html = ""
				if hour_count_source.source.start_text in html:
					html = html.split(hour_count_source.source.start_text, 1)[1]
				if hour_count_source.source.end_text in html:
					html = html.split(hour_count_source.source.end_text, 1)[0]
				print link
				if html != "":
					for kw in hour_count_source.hour_count.story.keywords():
						if " " + kw.keyword in html:
							count += 1
							print kw.keyword
							# add as StoryLink
							sl = StoryLink(url=link,
										   date=the_time,
										   title=item.find("title").text,
										   hour_count_source=hour_count_source)
							sl.save()
							break
	hour_count_source.count = count
	hour_count_source.save()


def in_last_hour(the_time):
	t = datetime.datetime.now()
	if the_time.year == t.year:
		if the_time.month == t.month:
			if the_time.day == t.day:
				if the_time.hour == t.hour:
					return False
				if the_time.hour == t.hour-1:
					return True
			if  the_time.day == t.day-1:
				if the_time.hour == 23 and t.hour == 0:
					return True
		if the_time.month == t.month-1:
			if the_time.day == calendar.monthrange(the_time.year,the_time.month)[1] and t.day == 1:
				if the_time.hour == 23 and t.hour == 0:
					return True
	if the_time.year == t.year-1:
		if the_time.month == 12 and t.month == 1:
			if the_time.day == calendar.monthrange(the_time.year,the_time.month)[1] and t.day == 1:
				if the_time.hour == 23 and t.hour == 0:
					return True
	return False

# cron job
def test():
	t = datetime.datetime.now()
	for story in Story.objects.all():
		hc = HourCount(story=story, date=t)
		hc.save()
		for source in Source.objects.all():
			hcs = HourCountSource(hour_count=hc, source=source, count=0)
			hcs.save()
			count_rss(hcs)

"""
def twitter_results(keyword, date_from, date_to):
	done = False
	
	#OAuth
	Consumer_Key = 'C6N8KWKBCTv4wJseyYY0i42CN'
	Consumer_Secret = 'dYodyKDuaVoqWsc6g4DoRT4oufgR0noxC1I5TJZs8KUA87oqYh'
	Access_Token = '25333458-MoYEifjzxjaxcp5e935W3qwPMCKJbgf6PbaMxKZC1'
	Access_Token_Secret = 'Ypy5HSk35vuncJo6KMXEyEqpBNfKNasfZ8qV6pavXHCKu'

	#Twitter API v1.1
	twitter = Twython(Consumer_Key, Consumer_Secret, Access_Token, Access_Token_Secret)
	response = twitter.search(q=keyword, count=100, since=date_from, until=date_to, result_type='mixed')

	#Results (partial)
	count_tweets = len(response['statuses']);

	#If all the tweets have been fetched, then we are done
	if not ('next_results' in response['search_metadata']): 
	    done = True

	#If not all the tweets have been fetched, then...
	while done == False:
	    #Parsing information for maxID
	    parse1 = response['search_metadata']['next_results'].split("&")
	    parse2 = parse1[0].split("?max_id=")
	    max_id = parse2[1]
	    #Twitter is queried (again, this time with the addition of 'max_id')
	    response = twitter.search(q=keyword, count=100, since=date_from,
	    						  until=date_to, max_id=max_id, include_entities=1,
	    						  result_type='mixed')

	    #Updating the total amount of tweets fetched
	    count_tweets = count_tweets + len(response['statuses'])

	    #If all the tweets have been fetched, then we are done
	    if not ('next_results' in response['search_metadata']): 
	        done = True
	return count_tweets
"""