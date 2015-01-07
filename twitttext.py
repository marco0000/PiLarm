#da alarmd3, funziona
#!/usr/bin/python

def sendtwitt(text):

	import subprocess
	import datetime
	import time
	import os 
	import tweetpony
	
	todays_date = datetime.datetime.today()
	api = tweetpony.API(consumer_key = "XXX", consumer_secret = "XXX", access_token = "XXX", access_token_secret = "XXX")

	user = api.user

	tweets = api.user_timeline(screen_name = "LoraMarco1")

	try:
			api.update_status(status = text)
	except tweetpony.APIError as err:
			print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
	else:
			print todays_date.strftime('%m-%d-%y-%H%M') + ";" + user.screen_name + ";" + text 
