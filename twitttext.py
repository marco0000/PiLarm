#da alarmd3, funziona
#!/usr/bin/python

def sendtwitt(text):

	import subprocess
	import datetime
	import time
	import os 
	import tweetpony
	
	todays_date = datetime.datetime.today()
	api = tweetpony.API(consumer_key = "Dz03dRqQeFpqSV8nfmVEzZvNl", consumer_secret = "hM9uQPU0RXfqXFPAYz5XagIM2ey484R4jMx80SUcTSB9viLK4n", access_token = "2730297008-wDRKtfP2YStutVP23hIs04fZRm1JTVFDgcbt93J", access_token_secret = "07ehHLAM6lcrT10D1WbBOzHZui5qbaufwxKBlzkcNzJIa")

	user = api.user

	tweets = api.user_timeline(screen_name = "LoraMarco1")

	try:
			api.update_status(status = text)
	except tweetpony.APIError as err:
			print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
	else:
			print todays_date.strftime('%m-%d-%y-%H%M') + ";" + user.screen_name + ";" + text 