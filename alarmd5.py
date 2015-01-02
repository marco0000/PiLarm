#!/usr/bin/python
from Adafruit_MCP230XX import Adafruit_MCP230XX
import subprocess
import datetime
import time
import os 
import RPi.GPIO as io
import tweetpony
import picamera

#DEFINIZIONE FUNZIONI
def sendtwitt(message, api):
	try:
			api.update_status(status = message)
	except tweetpony.APIError as err:
			print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
	else:
			print "TWITTER MESSAGE: " + message
			log(message)

def sendtwittmedia(message, api, path):
	try:
	        api.update_status_with_media(status = message, media= path)
	except tweetpony.APIError as err:
	        print "Oops, something went wrong! Twitter returned error #%i and said: %s" % (err.code, err.description)
	else:
			print "TWITTER MESSAGE: " + message
			log(message)

def takepicture(grab_cam, path):
	#grab_cam = picamera.PiCamera()
	#grab_cam.rotation = 180
	todays_date = datetime.datetime.today()
	grab_cam.capture(path)
	#grab_cam.close()
				
def log(text):
	with open("/home/pi/PiLarm/log.txt", "a") as fo:
		fo.write(text+"\n")
	fo.closed

def writefile(text, path):
	with open(path, "a") as fo:
		fo.write(text+"\n")
	fo.closed

def cleanfile(path):
	#cancella prima riga file twitt
	fo = open(path, "r")
	data_list = fo.readlines()
	fo.close()
	i=0
	for item in data_list:
		del data_list[0]
		i=i+1
	fo = open(path, "w")
	fo.writelines(data_list)
	fo.close()	

def readfile(path):
	with open(path, "r") as fo:
			fo.seek(0, 0)
			status = fo.read(1)
	fo.closed
	return status

def soundmotiondetect():
	subprocess.call("mpg123 /home/pi/PiLarm/motiondetect.mp3", shell=True)

def soundalarm():
	subprocess.call("mpg123 /home/pi/PiLarm/alarm.mp3", shell=True)

def soundsurrender():
	subprocess.call("mpg123 /home/pi/PiLarm/surrender.mp3", shell=True)

# --------- Main Program ---------

#INIZIALIZZO PATHs
path_armed="/home/pi/PiLarm/armed.txt"
path_log="/home/pi/PiLarm/log.txt"
path_twitt="/home/pi/PiLarm/twitt.txt"
path_status="/home/pi/PiLarm/status.txt"
cleanfile(path_status)

#INIZIALIZZO PI-CAMERA
grab_cam = picamera.PiCamera()
grab_cam.rotation = 180

#INIZIALIZZO TEWWTPONY
#CREDENZIALI GABBANESE
#api = tweetpony.API(consumer_key = "fWda91GYGNa6RgE65fYznhhzQ", consumer_secret = "3qjueaXS4fRs1BacS0Zj37ioOeoXhmB6FZGJqBwY40tTLmMbSY", access_token = "756822972-C9li9zb358QGEW6nYEdaxVxm5v1RVNRCDJSMFvFH", access_token_secret = "pmtaRQSQHCQyFAT68wQADMFQB2CTOoLgtRAQ3v8Q8lNr4")
#CREDENZIALI LoraMarco1
try:
	api = tweetpony.API(consumer_key = "Dz03dRqQeFpqSV8nfmVEzZvNl", consumer_secret = "hM9uQPU0RXfqXFPAYz5XagIM2ey484R4jMx80SUcTSB9viLK4n", access_token = "2730297008-wDRKtfP2YStutVP23hIs04fZRm1JTVFDgcbt93J", access_token_secret = "07ehHLAM6lcrT10D1WbBOzHZui5qbaufwxKBlzkcNzJIa")
	user = api.user
except:
	print "Ops, api not activated"
	
#INIZIALIZZO PIN GPIO-PI [solo OUTPUT]
io.setmode(io.BCM)

flashingLight_pin = 9
io.setup(flashingLight_pin, io.OUT)
io.output(flashingLight_pin, io.LOW)


#INIZIALIZZO PIN GPIO-A [MCP23017] [solo INPUT]
num_gpios = 16
mcp = Adafruit_MCP230XX(address = 0x20, num_gpios = 16) # MCP23017

#load sensor configuration from IOsetting.txt
with open("/home/pi/PiLarm/IOsetting.txt", "r") as fo:
	descr_pin= fo.next().strip().split( ',' )
fo.closed

#inizializzo pin GPIO-A come input con pull-up
print "-------------------------------------------------------------------"
j=0
todays_date = datetime.datetime.today()
now=todays_date.strftime('%d-%m-%y-%H:%M:%S')
for q in descr_pin:
	if (j <= num_gpios-1):
		print "PI-ALARM: " +  now + "; Port N. " + str(j) + ": " + descr_pin[j]
		mcp.config(j, mcp.INPUT)
		mcp.pullup(j, 1)
	else:
		print "PI-ALARM: " +  now + "; ERR: the number of sensors is higher than 16; sensor " + descr_pin[j] + " is not managed"
	j = j+1

#eccezioni per gestire BUTTON-1 e BUTTON-2 (normalmente aperti) tramite resistenza di pull-down
mcp.config(2, mcp.INPUT)
mcp.pullup(2, 0)
mcp.config(3, mcp.INPUT)
mcp.pullup(3, 0)
mcp.config(8, mcp.INPUT)

#verifico che il numero di sensori definiti in IOsetting.txt siano inferore al numero di GPIO-A
print "PI-ALARM: " +  now + "; GPIO-EX#1: " + str(j) + " GPIO ports used"
num_sensors= j
print "PI-ALARM: " +  now + "; Numero di sensori: " + str(num_sensors)
if (j>num_gpios):
	print "PI-ALARM: " +  now + "; " + str(j-num_gpios) + " sensors not managed"

#inizializzo vettori
previous_state=descr_pin[:]
current_state=descr_pin[:]
alarm_state=descr_pin[:]
alarm=descr_pin[:]

i=0
for item in descr_pin:
	previous_state[i]=int(0)
	current_state[i]=int(0)
	alarm_state[i]=int(0)
	alarm[i]=int(0)
	i=i+1

#ciclo main
while True:
	try:
		todays_date = datetime.datetime.today()
		now=todays_date.strftime('%d-%m-%y-%H:%M:%S')
	except:
		now="00-00-00-00:00:00"
		
	alarm_sum1=0
	alarm_sum2=0
	message1 ="PI-ALARM: " +  now + "; " + "RIEPILOGO ALLARMI ATTIVI: "
	message2 ="PI-ALARM: " + now + "; " + "RILEVATO  NUOVO  ALLARME: "
	print "------------------------------------------------------------------------"
	print now 
	
	i=0
	for item in descr_pin:
		current_state[i] = int(str(mcp.input(i) >> i))
		print "PI-ALARM: " +  now + "; " + "GPIO port N. " + str(i) + " stato= " + str(current_state[i]) + "  - " + str(descr_pin[i])
		if int(current_state[i])==1:
			alarm_sum1= alarm_sum1 + 1
			message1 = message1 + str(descr_pin[i]) +  "=" + str(current_state[i]) + "; "
			if int(previous_state[i])==0 and int(current_state[i])==1:
				alarm_sum2=alarm_sum2 + 1
				message2 = message2 + str(descr_pin[i]) +  "=" + str(current_state[i]) + "; "
		i=i+1
	if int(alarm_sum1)+int(alarm_sum2)>0:
		print "------------------------------------------------------------------------"
		if int(alarm_sum2)==0:
			print message1
			writefile(message1, path_log)
			cleanfile(path_status)
			writefile(message1, path_status)
		else:
			print message1
			print message2
			writefile(message1, path_log)
			writefile(message2, path_log)
			cleanfile(path_status)
			writefile(message1, path_status)
	else:
		cleanfile(path_status)
		writefile("NO ACTIVE ALARM", path_status)
	
	if alarm_sum2>0:
		status = readfile(path_armed)
		print "PI-ALARM: " +  now + "; Motion detected, armed status: " + str(status)
		if (status == "1"):
			print "PI-ALARM: " +  now + "; take a picture"
			path_picture = '/home/pi/PiLarm/pictures/'+ now + '.jpg'
			takepicture(grab_cam, path_picture)
			soundmotiondetect()
			print "PI-ALARM: " +  now + "; waiting for passcode...."
			time.sleep(5)
			status = readfile(path_armed)
			if (status == "1"):
				print "PI-ALARM: " +  now + "; Correct passcode not entered, twitting picture and sounding alarm."
				message = "PI-ALARM: " + now + "; " + "INTRUDER ALERT"
				try:
					sendtwittmedia(message, api, path_picture)
					sendtwitt(message1, api)
					sendtwitt(message2, api)
				except:
					print "PI-ALARM: " +  now + "; TWITTER not authenticated, messages cannot be sent"
				writefile(message, path_log)
				io.output(flashingLight_pin, io.HIGH)
				soundalarm()
				soundsurrender()
				soundalarm()                       
				io.output(flashingLight_pin, io.LOW)
	i=0
	for item in descr_pin:
		previous_state[i]=current_state[i]
		i = i+1
	#previous_pir=current_pir
	time.sleep(1)