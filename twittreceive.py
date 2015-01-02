#https://github.com/Mezgrman/TweetPony/blob/master/README.md
#!/usr/bin/env python
# Copyright (C) 2013 Julian Metzler
# See the LICENSE file for the full license.

"""
This script starts a user stream and displays new tweets.
"""

from _common import get_api
import tweetpony
import datetime
import time
import RPi.GPIO as GPIO
import subprocess
import send_email_via_gmail as gmail

#DEFINIZIONE FUNZIONI
def sendtwitt(message, api):
	try:
			api.update_status(status = message)
	except tweetpony.APIError as err:
			print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
	else:
			print "TWITTER MESSAGE: " + message
			log("TWITTER MESSAGE: " + message)

			
def sendmail(address, object, text, path):
	try:
			gmail.mail(address, object, text, path)
			message = "PI-ALARM: " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + ";" + user.screen_name + ";" + "SENDLOG: " + "sent"
			sendtwitt(message, api)
	except:
			print "Oops, something went wrong! Email returned error "
	else:
			print "E-mail sent to: " + address
			log("LOGFILE SENT VIA E-MAIL TO: " + address)	
	
			
def log(text):
	with open("/home/pi/PiLarm/log.txt", "a") as fo:
		fo.write(text+"\n")
	fo.closed

def cleanfile(path):
	#cancella prima riga file twitt
	fo = open("/home/pi/PiLarm/twitt.txt", "r")
	data_list = fo.readlines()
	fo.close()
	del data_list[0]
	fo = open(path, "w")
	fo.writelines(data_list)
	fo.close()

#INIZIALIZZO TEWWTPONY
#CREDENZIALI GABBANESE
api = tweetpony.API(consumer_key = "fWda91GYGNa6RgE65fYznhhzQ", consumer_secret = "3qjueaXS4fRs1BacS0Zj37ioOeoXhmB6FZGJqBwY40tTLmMbSY", access_token = "756822972-C9li9zb358QGEW6nYEdaxVxm5v1RVNRCDJSMFvFH", access_token_secret = "pmtaRQSQHCQyFAT68wQADMFQB2CTOoLgtRAQ3v8Q8lNr4")
#CREDENZIALI LoraMarco1
api = tweetpony.API(consumer_key = "Dz03dRqQeFpqSV8nfmVEzZvNl", consumer_secret = "hM9uQPU0RXfqXFPAYz5XagIM2ey484R4jMx80SUcTSB9viLK4n", access_token = "2730297008-wDRKtfP2YStutVP23hIs04fZRm1JTVFDgcbt93J", access_token_secret = "07ehHLAM6lcrT10D1WbBOzHZui5qbaufwxKBlzkcNzJIa")
user = api.user

attempt = "0000"
passcode = "1912"    
haltcode = "5764"
sendlog = "1111"
sendstatus = "2222"

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(11, GPIO.OUT) #Green
GPIO.output(11, GPIO.HIGH)
GPIO.setup(10, GPIO.OUT) #Red
GPIO.output(10, GPIO.LOW)
GPIO.setup(9, GPIO.OUT) #Flashing Light
GPIO.output(9, GPIO.LOW)
	
	
class StreamProcessor(tweetpony.StreamProcessor):
	def on_status(self, status):
		command = str(status.text)
		if "PI-ALARM" in command:
			print "twitt inviato da PI-ALARM"
		else:
			#PRINT COMANDO E SALVATAGGIO IN TWITT.TXT
			todays_date = datetime.datetime.today()
			message = "COMMAND : " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + ";" + status.user.screen_name + ";" + command
			print message
			log(message)
			path = "/home/pi/PiLarm/twitt.txt"
			cleanfile(path)
			with open("/home/pi/PiLarm/twitt.txt", "r+") as fo:
				fo.seek(0, 0)
				fo.write(command)
			fo.closed
			#ESEGUI COMANDI
			if passcode in command:
				with open("/home/pi/PiLarm/armed.txt", "r+") as fo:
					fo.seek(0, 0)
					status = fo.read(1)
				fo.closed
				if (status == "1"):
					#system was armed, disarm it
					with open("/home/pi/PiLarm/armed.txt", "r+") as fo:
						fo.seek(0, 0)
						fo.write("0")
					fo.closed
					GPIO.output(11, GPIO.HIGH) #Green LED On
					GPIO.output(10, GPIO.LOW) #Red LED off
					GPIO.output(9, GPIO.LOW)
					subprocess.call("mpg123 /home/pi/PiLarm/disarmed.mp3", shell=True)
					todays_date = datetime.datetime.today()
					message = "PI-ALARM: " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + ";" + user.screen_name + ";" + "SENDSTATUS: " + "DISARMED"
					sendtwitt(message, api)
				else:
					GPIO.output(11, GPIO.LOW) #Green LED Off
					GPIO.output(10, GPIO.HIGH) #Red LED on
					subprocess.call("mpg123 /home/pi/PiLarm/armed.mp3", shell=True)
					todays_date = datetime.datetime.today()
					message = "PI-ALARM: " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + ";" + user.screen_name + ";" + "SENDSTATUS: " + "ARMED"
					sendtwitt(message, api)
					time.sleep(5)
					with open("/home/pi/PiLarm/armed.txt", "r+") as fo:
						fo.seek(0, 0)
						fo.write("1")
					fo.closed
			if haltcode in command:
				subprocess.call("mpg123 /home/pi/PiLarm/shutdown.mp3", shell=True)
				subprocess.call("halt", shell=True)
			if sendlog in command:
				print "sending log.txt file to m.andrenacci@gmail.com"
				todays_date = datetime.datetime.today()
				sendmail( "sandroni.laura@gmail.com", todays_date.strftime('%d-%m-%y-%H:%M:%S')+ "PI-ALARM: log.txt", "PI-ALARM: log.txt", "/home/pi/PiLarm/log.txt")
				print "E-mail sent to: " + "sandroni.laura@gmail.com"
				log("LOGFILE SENT VIA E-MAIL TO: " + "sandroni.laura@gmail.com")
				sendmail( "m.andrenacci@gmail.com", todays_date.strftime('%d-%m-%y-%H:%M:%S')+ "PI-ALARM: log.txt", "PI-ALARM: log.txt", "/home/pi/PiLarm/log.txt")
				print "E-mail sent to: " + "m.andrenacci@gmail.com"
				log("LOGFILE SENT VIA E-MAIL TO: " + "m.andrenacci@gmail.com")
			if sendstatus in command:
				with open("/home/pi/PiLarm/armed.txt", "r+") as fo:
					fo.seek(0, 0)
					status = fo.read(1)
				fo.closed
				todays_date = datetime.datetime.today()
				if (status == "1"):
					message = "armed"
				else:
					message = "disarmed"
				message = "PI-ALARM: " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + "; " + "SENDSTATUS: " + message
				sendtwitt(message, api)
				with open("/home/pi/PiLarm/status.txt", "r+") as fo:
					fo.seek(0, 0)
					message = fo.read()
				fo.closed
				message =  "PI-ALARM: " + todays_date.strftime('%d-%m-%y-%H:%M:%S') + "; " + "SENDSTATUS: " + message
				sendtwitt(message, api)
			#INSERIRE QUI ALTRI COMANDI
			#commands
			return True

def main():
	api = get_api()
	if not api:
		return
	processor = StreamProcessor(api)
	try:
		api.user_stream(processor = processor)
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	main()