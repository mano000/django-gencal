import datetime
import calendar
import string
from django import template

register = template.Library()

@register.inclusion_tag('gencal/gencal.html')
def gencal(date = datetime.datetime.now(), cal_items=[]):
	""" 
	This will generate a calendar. It expects the year & month (in datetime format)
	and a list of dicts in the following format:
	
	cal_items = [{ 'day':datetime(2008,1,30), 'title':"Concert at Huckelberries", 'class':"concert",    'url':'/foo/2' }, 
	             { 'day':datetime(2008,2,4),  'title':"BBQ at Mom\'s house",      'class':"restaurant", 'url':'/restaurants/9' }]
	
	A listing of variables and their meanings:
	
	* day is the datetime of the day you'd like to reference
	* url is the url to the object you'd like to reference
	* title is the text of the event that will be rendered
	* class is a non-necessary field that will apply class="your_entry" to the list item
	
	My suggested urls.py file is:
	*Note: Its important to name your year/month url gencal or the backwards/forwards links won't work*;
	
	::
	
		urlpatterns = patterns('',
			url(r'^(?P<year>\d{4})/(?P<month>\d+)/$', 'online_department.schedule.views.index', name='gencal'),
			(r'^$', 'online_department.schedule.views.index'),
		)
		
	The CSS I use to make it look good is:
	
	::
	
		<style type="text/css">
		table.cal_month_calendar caption { text-align: center; text-size: 15px; background: none;}
		table.cal_month_calendar table { width: 455px;}
		table.cal_month_calendar th,td { width: 65px;}
		table.cal_month_calendar th { text-align: center; }
		table.cal_month_calendar td { height: 65px; position: relative;}
		table.cal_month_calendar td.cal_not_in_month { background-color: #ccc;}
		table.cal_month_calendar div.table_cell_contents { position: relative; height: 65px; width: 65px;}
		table.cal_month_calendar div.month_num { position: absolute; top: 1px; left: 1px; }
		table.cal_month_calendar ul.event_list { list-style-type: none; padding: 15px 0 0 0; margin: 0;}
		table.cal_month_calendar { border-collapse: collapse; }
		table.cal_month_calendar th { color: white; background: black;}
		table.cal_month_calendar td, th { border: 1px solid black; }
		</style>
	
	"""
	# Set the values pulled in from urls.py to integers from strings
	year = date.year
	month = date.month
	
	# account for previous month in case of Jan
	if month-1 == 0:
		lastmonth = 12
		prev_date = datetime.datetime(year-1, 12, 1)
	else:
		lastmonth = month-1
		prev_date = datetime.datetime(year, month-1, 1)
	
	if month+1 == 13:
		next_date = datetime.datetime(year+1, 1, 1)
	else:
		next_date = datetime.datetime(year, month+1, 1)
			
	month_range = calendar.monthrange(year, month)
	first_day_of_month = datetime.date(year, month, 1)
	last_day_of_month = datetime.date(year, month, month_range[1])
	num_days_last_month = calendar.monthrange(year, lastmonth)[1]
	# first day of calendar is:
	#
	# first day of the month with days counted back (timedelta)
	# until Sunday which is day-of-week_num plus one (for the
	# 0 offset) 
	#
	
	first_day_of_calendar = first_day_of_month - datetime.timedelta(first_day_of_month.weekday())
	
	# last day of calendar is:
	# 
	# the last day of the month with days added on (timedelta) 
	# until saturday[5] (the last day of our calendar)
	#
	
	last_day_of_calendar = last_day_of_month + datetime.timedelta(12 - last_day_of_month.weekday())
	
	month_cal = []
	week = []
	week_headers = []
	for header in calendar.weekheader(2).split(' '):
		week_headers.append(header)
	day = first_day_of_calendar
	while day <= last_day_of_calendar:

		cal_day = {} 				# Reset the day's values
		cal_day['day'] = day		# Set the value of day to the current day num
		cal_day['event'] = []		# Clear any events for the day
		for event in cal_items:		# iterate through every event passed in
			if event['day'].strftime("%m %d") == day.strftime("%m %d"):	# Search for events whose day matches the current day. Be insensitive to extra datetime params. Only look for month + date
				cal_day['event'].append({'title':event['title'], 'url':event['url'], 'class':event['class']}) # If it is happening today, add it to the list
		if day.month == month:		# Figure out if the day is the current month, or the leading / following calendar days
			cal_day['in_month'] = True
		else:
			cal_day['in_month'] = False
		week.append(cal_day)		# Add the current day to the week
		if day.weekday() == 6:		# When Sunday comes, add the week to the calendar
			month_cal.append(week)	
			week = []				# Reset the week
		day += datetime.timedelta(1) 		# set day to next day (in datetime object)
		
	
	return {'month_cal': month_cal, 'headers': week_headers, 'date':date, 'prev_date':prev_date, 'next_date':next_date }