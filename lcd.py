#!/usr/bin/env python

from Adafruit_CharLCD import Adafruit_RGBCharLCD as rgblcd 
import RPi.GPIO as GPIO
from daemon import Daemon
import requests
import time

LCD_COLUMNS = 16
LCD_ROWS = 2 

RSPIN = 19 
EPIN = 6
D4PIN = 12
D5PIN = 16
D6PIN = 26
D7PIN = 21
RPIN = 7
GPIN = 5
BPIN = 13

KEY1PIN = 27
KEY2PIN = 17
KEY3PIN = 23
KEY4PIN = 4

FAST_LOOPDT = 1
SLOW_LOOPDT = 60
BACKLIGHT_TIMEOUT = 30

# Special characters
DEGC = "\337C"

# Message templates
MSG_DEFAULT = "Temperature: {}" + DEGC + "\nHumidity: {}%"
MSG_TIME = "Today is:\n{}"
MSG_PRESSURE = "Pressure:\n{}hPa"
MSG_LUX = "Lux level:\n {}lx"
MSG_ALTITUDE = "Altitude: ()m"
MSG_TIMESTAMP = "Time since epoch\n{}"

LATEST_OBS_URL = "http://localhost/api/latest"

class ObsLCD:
    """
    Class to represent the LCD and 4 button keypad used to get realtime feed back
    for the weather station without checking the web interface.

    States: 
    0b00000001 - Default message on screen LCD off
    0b00000010 - LCD ON - starts timer for BACKLIGHT_TIMEOUT
    0b00000100 - Today
    0b00001000 - Pressure
    0b00010000 - Lux
    0b00100000 - Altitude
    0b01000000 - Timestamp
    0b10000000 - Scroll
    """


    def Run(self):
        self.Setup()

        while True:
            self.Loop()

    def Setup(self):
        self._lcd = rgblcd(RSPIN, EPIN, D4PIN, D5PIN, D6PIN, D7PIN, LCD_COLUMNS, LCD_ROWS, RPIN, GPIN, BPIN)
        self._gpio = self.lcd._gpio
        self._bltimeout = time.time()
        self._state = 0xb00000001
        
        self._latest = {}

        # loop vars
        self._slowtime = time.time()
        self._fasttime = time.time()

        self._gpio.add_event_detect(KEY1PIN, GPIO.FALLING, callback=callback, bouncetime=300)
        self._gpio.add_event_detect(KEY2PIN, GPIO.FALLING, callback=callback, bouncetime=300)
        self._gpio.add_event_detect(KEY3PIN, GPIO.FALLING, callback=callback, bouncetime=300)
        self._gpio.add_event_detect(KEY4PIN, GPIO.FALLING, callback=callback, bouncetime=300)

        self._keys = list()

    def Loop(self):
        # Fast loop
        if self._fasttime >= time.time():
            # Check LCD timout
            if self._lcdon:
                if lcd._bltimeout > time.time():
                    self._lcdon = False
                    lcd.set_color(0,0,0)
            # Add the Delta time for our fast loop
            self._fasttime += FAST_LOOPDT

        # Slow loop
        if self._slowtime >= time.time():
            if self._state == 0:
                # Update messages with the lastest weather observation data point
                self.SetupMessages(self.GetLatest())


            # Add the Delta time for our slow loop
            self._slowtime += SLOW_LOOPDT
            

    def SetupMessages(self, obsPoint):
        self._lastMessage = self._message
        self._message = line1 + "\n" + line2
        

    def GetLatest(self):
        r = requests.get(LATEST_OBS_URL)

        if r.status_code == 200:
            return True, r.json() 
        else:
            return False, "API returned\nStatus code {}".format(r.status_code)

    def ProcessKeys(self, keys):
        
        if len(keys) > 0:
            # Update the backlight timeout 
            if self._lcdon == False:
                self._lcdon = True
                self._bltimeout = time.time() + BACKLIGHT_TIMEOUT
            else:
                # Process each key that has been pressed
                for key in keys:
                    if key == KEY1PIN:
                        pass
                    elif key == KEY2PIN:
                        pass
                    elif key == KEY3PIN:
                        pass
                    elif key == KEY4PIN:
                        pass

    def ToggleBacklight(self):
        if self._lcdon:
            self._gpio.setup(RPIN, GPIO.IN)
            self._gpio.setup(GPIN, GPIO.IN)
            self._gpio.setup(BPIN, GPIO.IN)
        else:
            self._gpio.setup(RPIN, GPIO.OUT)
            self._gpio.setup(GPIN, GPIO.OUT)
            self._gpio.setup(BPIN, GPIO.OUT)

    def Callback(self, pin):
        self._keys.append(pin)

#if __name__ == "__main__":
#        daemon = lcd('/tmp/lcd-daemon.pid')
#        if len(sys.argv) == 2:
#                if 'start' == sys.argv[1]:
#                        daemon.start()
#                elif 'stop' == sys.argv[1]:
#                        daemon.stop()
#                elif 'restart' == sys.argv[1]:
#                        daemon.restart()
#                else:
#                        print "Unknown command"
#                        sys.exit(2)
#                sys.exit(0)
#        else:
#                print "usage: %s start|stop|restart" % sys.argv[0]
#                sys.exit(2)
