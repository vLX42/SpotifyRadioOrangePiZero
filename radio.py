import os
from pyA20.gpio import gpio
	
from pyA20.gpio import port
import time
import sched
import subprocess
import sys
import requests
import json
import textwrap
import json

#from oled.device import ssd1306, sh1106
#from oled.render import canvas

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106



from time import sleep
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import PIL.ImageOps 


sp_config = {
				'client'	: '127.0.0.1',
				'port'		: '4000',
				'status'	: ('/api/info/status',	 'i'),
				'metadata': ('/api/info/metadata', 'i'),
				'pause'	 : ('/api/playback/pause','p'),
				'play'		: ('/api/playback/play', 'p'),
				'next'		: ('/api/playback/next', 'p'),
				'prev'		: ('/api/playback/prev', 'p')
}



#adjust for where your switch is connected
buttonPin1 = port.PA0
#38
buttonPin2 = port.PA7
#37
buttonPin3 = port.PA1
#36
buttonPin4 = port.PA6
#35


#GPIO.setup(buttonPin3,GPIO.IN)
#GPIO.setup(buttonPin4,GPIO.IN)
playIndex = 0
playMax = 0

onoffDelay = 0
onoffDelayMax = 5

spotifyTitle = 0
spotifyTitleMax = 10

playingRadio = False
bSpotify = False
bShowSpotifyLogo = False
bSpeakerOn = True



#disp = sh1106(port=0, address=0x3C)

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=0, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
disp = sh1106(serial, rotate=2)


#GPIO.setmode(GPIO.BCM)


gpio.init() 


#GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(buttonPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(buttonPin3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(buttonPin4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
gpio.setcfg(buttonPin1, gpio.INPUT)
gpio.setcfg(buttonPin2, gpio.INPUT)
gpio.setcfg(buttonPin3, gpio.INPUT)
gpio.setcfg(buttonPin4, gpio.INPUT)

gpio.pullup(buttonPin1, gpio.PULLDOWN) #Enable pull-up
gpio.pullup(buttonPin2, gpio.PULLDOWN) #Enable pull-up
gpio.pullup(buttonPin3, gpio.PULLDOWN) #Enable pull-up
gpio.pullup(buttonPin4, gpio.PULLDOWN) #Enable pull-up


def createPlayList():
	subprocess.call("mpc clear" , shell=True)
	for radiostation in json_radio:
		subprocess.call("mpc add " + radiostation['Url'] , shell=True)
	for i in range(playMax):
		subprocess.call("mpc play " + str(i) + " & sleep 0.1 & mpc stop ", shell=True)
	subprocess.call("mpc stop ", shell=True)


with open('radio.json') as json_data:
    json_radio = json.load(json_data)
	
playMax = len(json_radio)-1

createPlayList()


def speakerOn():
	bSpeakerOn = True
	#GPIO.output(ledPin, GPIO.HIGH)

def speakerOff():
	bSpeakerOn = False
	DisplayClear()
	#GPIO.output(ledPin, GPIO.LOW)

def displaySpoitfyTitle():

	# Write some text.
	text = "    -=SPOTIFY=-        " +  spconnect('metadata','track_name')  +" - " + spconnect('metadata','artist_name')
	#print text
		
	lines = textwrap.wrap(text, width=24)
	current_h, pad = 0, 0

	font = ImageFont.load_default()
	font2 = ImageFont.truetype('fonts/C&C Red Alert [INET].ttf', 12)
	with canvas(disp) as draw:
		for line in lines:
			w, h = draw.textsize(line, font=font2)
			draw.text(((128 - w) / 2, current_h), line, font=font2, fill=255)
			current_h += h + pad

	
def spconnect (command, parameter): 


	# send http request to get data from spotify client
	sOut = ''
	try:
		rdata = requests.get('http://'+ sp_config['client'] + ':' + sp_config['port'] + sp_config[command][0])
		if rdata.ok : 
			if sp_config[command][1] == 'p' :
				sOut += 'OK'
			else :
				if not parameter :
					for parameter,pvalue in rdata.encode('utf-8').json().items():
						sOut +=	('%s : %s' % (parameter, pvalue))
				else :
					sOut +=	str(rdata.json()[parameter])
		else :
			sOut +=	('Error: %s' % rdata.status_code)
	
	except requests.exceptions.ConnectionError as error:
		sOut +=	('Connection Error: %s' % error)
	except requests.exceptions.HTTPError as error:
		sOut +=	('HTTP Error: %s' % error)
	except:
		sOut += "Unknown error"
	return sOut

def mpcPlaying (): 
	cmd = subprocess.Popen("mpc status",shell=True, stdout=subprocess.PIPE)
	status = cmd.stdout.readlines()
	if "[playing]" in str(status):
		return True
	else:
		return False

def PlayStation(url):
	subprocess.call("mpc clear & mpc add " + url + " & sleep 0.5 & mpc play 1", shell=True)

def PlayStationNo(playing):
	print str(playing)
	subprocess.call("mpc play " + str(playing+1) , shell=True)


def StopAll(channel):
	time.sleep(0.01)         # need to filter out the false positive of some power fluctuation
	if gpio.input(channel) != 1:
		return       
	print "Stop All!!"
	subprocess.call("mpc stop", shell=True)
	spconnect('pause','')
	speakerOff()

def DisplayClear():
	print "blank"
	with canvas(disp) as draw:
		logo = Image.open('logos/blank.pbm')
		draw.bitmap((0, 0), logo, fill=1)



def DisplayImage(file):

	with canvas(disp) as draw:
		logo = Image.open(file)
		logo = logo.convert('L')
		logo = PIL.ImageOps.invert(logo)
		logo = logo.convert('1')
		draw.bitmap((0, 0), logo, fill=1)
#	global playingRadio
#	global bSpotify
#	if playingRadio:
#		bSpotify = True
#		playingRadio = False
#	else:
#		bSpotify = False	

def TogglePlay(channel):
	time.sleep(0.01)         # need to filter out the false positive of some power fluctuation
	if gpio.input(channel) != 1:
		return      
	global playingRadio
	global bSpotify
	if playingRadio:
		print "switch to spotify"
		subprocess.call("mpc stop", shell=True)
		spconnect('play','') 
		bSpotify = True
		playingRadio = False
		bShowSpotifyLogo = False
	else:
		print "switch to radio"
		bSpotify = False
		PlayRadio(channel)
		#bSpotify = False
		#playingRadio = True
	speakerOn()	
	
def PlayRadio(channel):
	time.sleep(0.01)         # need to filter out the false positive of some power fluctuation
	if gpio.input(channel) != 1:
		return    
	if bSpotify:
		print "spotify command"
		if (channel==buttonPin1):
			spconnect('next','')
		if (channel==buttonPin2):
			spconnect('prev','')
		displaySpoitfyTitle()
	else:
		print "Radio tryk start"
		# Internal button, to open the gate
		global playIndex
		global playingRadio
		global bShowSpotifyLogo
		global json_radio
		bPlay = False
		#assuming the script to call is long enough we can ignore bouncing
		
		if (channel==buttonPin3):
			print 'Start Radio Pin ' + str(buttonPin3)
			bPlay = True
			spconnect('pause','')
		if (channel==buttonPin1):
			print 'Pin ' + str(buttonPin1)
			playIndex += 1
			bPlay = True
		if (channel==buttonPin2):
			print 'Pin ' + str(buttonPin2)
			playIndex -= 1
			bPlay = True
		if bPlay == True:
			if playIndex < 0:
				playIndex = playMax
			if playIndex > playMax:
				playIndex = 0
			print playIndex
			print json_radio[playIndex]['Name']
			#PlayStation(json_radio[playIndex]['Url'])
			PlayStationNo(playIndex)
			DisplayImage(json_radio[playIndex]['Logo'])
			
			bShowSpotifyLogo = False
			playingRadio = True
			speakerOn()
		#print "event end"

def loop(sc):
	global bSpotify
	global playingRadio
	global bShowSpotifyLogo
	global onoffDelay
	global spotifyTitle
	
	if spconnect('status','playing')=="True":
		bSpotify = True 
		#ImageLoad = True
		if bShowSpotifyLogo == False:
			print 'logos/spotify.pbm'
			DisplayImage('logos/spotify.pbm')
			bShowSpotifyLogo = True
		
		if (mpcPlaying()):
			playingRadio = True
		if playingRadio:
			print "playingRadio"
			print "spotify stop"
			playingRadio = False 
			subprocess.call("mpc pause", shell=True)
			spconnect('pause','')
			spconnect('play','') 
		speakerOn()
		spotifyTitle +=1
		if spotifyTitle >= spotifyTitleMax:
			displaySpoitfyTitle()
			spotifyTitle = 0
	else:
		bSpotify = False
		onoffDelay +=1
		if onoffDelay >= onoffDelayMax:
			if (mpcPlaying()):
				speakerOn()
				playingRadio = True

			else:
				speakerOff()
			onoffDelay = 0
	s.enter(0.5, 2, loop, (sc,))	
#GPIO.add_event_detect(buttonPin2, GPIO.BOTH, callback=PlayRadio, bouncetime=600)
#GPIO.add_event_detect(buttonPin, GPIO.BOTH, callback=PlayRadio, bouncetime=600)
#GPIO.add_event_detect(buttonPin3, GPIO.BOTH, callback=TogglePlay, bouncetime=600)
#GPIO.add_event_detect(buttonPin4, GPIO.BOTH, callback=StopAll, bouncetime=600)


s = sched.scheduler(time.time, time.sleep)
def do_buttomcheck(sc): 
		# do your stuff
		if gpio.input(buttonPin2) == 1:
			print "button 2"
			PlayRadio(buttonPin2)
		#GPIO.add_event_detect(buttonPin2, GPIO.BOTH, callback=PlayRadio, bouncetime=600)
		if gpio.input(buttonPin1) == 1:
			print "button 1"
			PlayRadio(buttonPin1)
		#GPIO.add_event_detect(buttonPin1, GPIO.BOTH, callback=PlayRadio, bouncetime=600)
		if gpio.input(buttonPin3) == 1:
			print "button 3"
			TogglePlay(buttonPin3)
		#GPIO.add_event_detect(buttonPin3, GPIO.BOTH, callback=TogglePlay, bouncetime=600)
		if gpio.input(buttonPin4) == 1:
			print "button 4"
			StopAll(buttonPin4)
		#GPIO.add_event_detect(buttonPin4, GPIO.BOTH, callback=StopAll, bouncetime=600)
		s.enter(0.015, 1, do_buttomcheck, (sc,))
			
s.enter(0.015, 1, do_buttomcheck, (s,))
s.enter(0.5, 2, 	loop, (s,))
s.run()
	
#while True:
#	print "start loop"
#	loop()
#	# Here everythink to loop normally
#	sleep(1);
#	
#GPIO.cleanup()
