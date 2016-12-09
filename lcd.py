#!/usr/bin/env python

from Adafruit_CharLCD import Adafruit_RGBCharLCD as rgblcd 
import RPi.GPIO as gpio
from daemon import Daemon
import requests
import time
from datetime import datetime as dt
import subprocess

# LCD size
LCD_COLUMNS = 16
LCD_ROWS = 2 

# LCD GPIO pins
RSPIN = 19 
EPIN = 6
D4PIN = 12
D5PIN = 16
D6PIN = 26
D7PIN = 21
RPIN = 7
GPIN = 5
BPIN = 13

# Keypad GPIO pins
KEY1PIN = 27
KEY2PIN = 17
KEY3PIN = 23
KEY4PIN = 4

FAST_LOOPDT = 1
SLOW_LOOPDT = 300
BACKLIGHT_TIMEOUT = 10

# Special characters
DEGC = "\337C"

# Message templates
MSG_DEFAULT = "Temperature: {temp:.0f}" + DEGC + "\nHumidity: {rhum}%"
MSG_TIME = "Today is:\n{}"
MSG_PRESSURE = "Pressure:\n{pres:.0f} hPa"
MSG_LUX = "Lux level:\n {lux:.0f} lx"
MSG_ALTITUDE = "Altitude: {alt:.0f}m"
MSG_TIMESTAMP = "Observation at:\n{}"
MSG_IP = "{}"

NUM_MSG_STATES = 6

SCROLL_TIME = 5

LATEST_OBS_URL = "http://localhost/api/latest"

ERR_NO_POINTS = 0
ERR_SHOW_IP = 1
ERR_NO_ERROR = 2

STATE_ERROR = 0
STATE_DEFAULT = 1
STATE_TIME = 2
STATE_PRESSURE = 3
STATE_LUX = 4
STATE_ALTITUDE = 5
STATE_TIMESTAMP = 6
STATE_SCROLL = 7
STATE_OTHER = 99

class ObsLCD:
    """
    Class to represent the LCD and 4 button keypad used to get realtime feed back
    for the weather station without checking the web interface.

    States: 
    0 - Error state, message varies
    1 - Default message on screen LCD off
    2 - Today
    3 - Pressure
    4 - Lux
    5 - Altitude
    6 - Timestamp
    7 - Scroll
    """

    def Run(self):
        try:
            self.Setup()

            while True:
                self.Loop()
        except KeyboardInterrupt:
            pass
        finally:
            gpio.cleanup()

    def Setup(self):
        self._lcd = rgblcd(RSPIN, EPIN, D4PIN, D5PIN, D6PIN, D7PIN, LCD_COLUMNS, LCD_ROWS, RPIN, GPIN, BPIN)
        self._bltimeout = time.time() + BACKLIGHT_TIMEOUT
        self._lcdon = True
        self._laststate = STATE_OTHER
        self._state = STATE_ERROR
        self._error = ERR_SHOW_IP
        self._errAck = False
        
        self._latest = {}

        # Loop timing
        self._slowtime = time.time()
        self._fasttime = time.time()

        # Setup keypad 
        for pin in (KEY1PIN, KEY2PIN, KEY3PIN, KEY4PIN):
            gpio.setup(pin, gpio.IN, pull_up_down=gpio.PUD_UP)

        gpio.add_event_detect(KEY1PIN, gpio.FALLING, callback=self.Callback, bouncetime=500)
        gpio.add_event_detect(KEY2PIN, gpio.FALLING, callback=self.Callback, bouncetime=500)
        gpio.add_event_detect(KEY3PIN, gpio.FALLING, callback=self.Callback, bouncetime=500)
        gpio.add_event_detect(KEY4PIN, gpio.FALLING, callback=self.Callback, bouncetime=500)

        self._keys = list()
        self._msgIP = MSG_IP.format(subprocess.check_output('./ip.sh'))

        self._scrolltime = time.time()

        self._message = STATE_ERROR
        self.SetupMessages()

    def Loop(self):
        # Fast loop
        if self._fasttime <= time.time():
            # Process key input
            self.ProcessKeys()

            # Update display with message based on state
            self.ProcessState()

            # If our state has changed we need to display the new message
            if self._laststate != self._state:
                self.DisplayMessage()

            # Check LCD timout if the lcd is currently on
            if self._lcdon:
                if self._bltimeout < time.time():
                    self.ToggleBacklight()
            
            # Save our current state as the last state. This lets
            # us avoid rendering if we dont change state next loop
            self._laststate = self._state

            # Add the Delta time for our fast loop
            self._fasttime += FAST_LOOPDT

        # Slow loop
        if self._slowtime <= time.time():
            # Update messages with the lastest weather observation data point
            self.SetupMessages()

            # Add the Delta time for our slow loop
            self._slowtime += SLOW_LOOPDT
            
    def SetupMessages(self):
        '''
        1 - MSG_DEFAULT = "Temperature: {}" + DEGC + "\nHumidity: {}%"
        2 - MSG_TIME = "Today is:\n{}"
        3 - MSG_PRESSURE = "Pressure:\n{}hPa"
        4 - MSG_LUX = "Lux level:\n {}lx"
        5 - MSG_ALTITUDE = "Altitude: ()m"
        6 - MSG_TIMESTAMP = "Time since epoch\n{}"
        '''
        self.GetLatest()
        if all (key in self._latest for key in ("temp", "rhum", "pres", "lux", "alt", "time")):
            self._msgDefault = MSG_DEFAULT.format(**self._latest)
            self._msgTime = MSG_TIME.format(dt.today().strftime('%d-%m-%y : %H:%M'))
            self._msgPres = MSG_PRESSURE.format(**self._latest)
            self._msgLux = MSG_LUX.format(**self._latest)
            self._msgAlt = MSG_ALTITUDE.format(**self._latest)
            self._msgTimestamp = MSG_TIMESTAMP.format(" ".join(dt.fromtimestamp(self._latest['time']).isoformat().split('T')))
        else:
            self._msgError = "Latest Points\nNot Found!"
            self._state = STATE_ERROR

    def DisplayMessage(self):
        self._lcd.clear()
            self._lcd.message(self._message)

    def ProcessState(self):
        if self._state == STATE_ERROR:
            if self._error == ERR_SHOW_IP:
                self._message = self._msgIP
            else:
                self._message = self._msgError

            if self._errAck:
                self._state = STATE_DEFAULT
                self._message = self._msgDefault
                if self._error == ERR_NO_POINTS:
                    self.SetupMessages()
                elif self._error == ERR_SHOW_IP:
                    self._error = ERR_NO_ERROR

                self.errAck = False
        elif self._state == STATE_DEFAULT:
            self._message = self._msgDefault
        elif self._state == STATE_TIME:
            self._message = self._msgTime
        elif self._state == STATE_PRESSURE:
            self._message = self._msgPres
        elif self._state == STATE_LUX:
            self._message = self._msgLux
        elif self._state == STATE_ALTITUDE:
            self._message = self._msgAlt
        elif self._state == STATE_TIMESTAMP:
            self._message = self._msg
        elif self._state == STATE_SCROLL:
            # If current screen has been displayed for
            # SCROLL_TIME swap to the next one
            if self._scrolltime < time.time():
                self._scroll += 1
                if self._scroll > NUM_MSG_STATES:
                    self._scroll = STATE_DEFAULT
                self._scrolltime += SCROLL_TIME
                self._laststate = STATE_OTHER 
                self._bltimeout = time.time() + BACKLIGHT_TIMEOUT

                # Update self._message to the newly scrolled to message
                if self._scroll == STATE_DEFAULT:
                    self._message = self._msgDefault
                elif self._scroll == STATE_TIME:
                    self._message = self._msgTime
                elif self._message == STATE_PRESSURE:
                    self._message = self._msgPres
                elif self._message == STATE_LUX:
                    self._message = self._msgLux
                elif self._message == STATE_ALTITUDE:
                    self._message = self._msgAlt
                elif self._message == STATE_TIMESTAMP:
                    self._message = self._msgTimestamp

    def GetLatest(self):
        r = requests.get(LATEST_OBS_URL)

        if r.status_code == 200:
            self._latest = r.json() 
        else:
            self._latest = {}

    def ProcessKeys(self):
        if len(self._keys) > 0:
            # Update the backlight timeout 
            if self._lcdon == False:
                self.ToggleBacklight()
            elif self._state == STATE_SCROLL:
                self._state = STATE_DEFAULT
            else:
                # Process each key that has been pressed
                for key in self._keys:
                    print key
                    if key == KEY1PIN:
                        if self._state == STATE_DEFAULT:
                            self._state = NUM_MSG_STATES
                        else:
                            self._state -= 1
                    elif key == KEY2PIN:
                        if self._state == NUM_MSG_STATES:
                            self._state = STATE_DEFAULT
                        else:
                            self._state += 1
                    elif key == KEY3PIN:
                        # Set scrolltime to now, set the scroll state and 
                        # reset the scroll screen
                        self._scrolltime = time.time()
                        self._state = STATE_SCROLL
                        self._scroll = 0
                    elif key == KEY4PIN:
                        self._errAck = True

            # Update backlight timeout if a key was pressed
            self._bltimeout = time.time() + BACKLIGHT_TIMEOUT

        self._keys=[]

    def ToggleBacklight(self):
        if self._lcdon:
            gpio.setup(RPIN, gpio.IN)
            gpio.setup(GPIN, gpio.IN)
            gpio.setup(BPIN, gpio.IN)
        else:
            gpio.setup(RPIN, gpio.OUT)
            gpio.setup(GPIN, gpio.OUT)
            gpio.setup(BPIN, gpio.OUT)
        self._lcdon = not self._lcdon

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
