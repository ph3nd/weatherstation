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
SLOW_LOOPDT = 60
BACKLIGHT_TIMEOUT = 10

# Special characters
DEGC = "\337C"

# Message templates
MSG_DEFAULT = "Temperature: {}" + DEGC + "\nHumidity: {}%"
MSG_TIME = "Today is:\n{}"
MSG_PRESSURE = "Pressure:\n{}hPa"
MSG_LUX = "Lux level:\n {}lx"
MSG_ALTITUDE = "Altitude: {}m"
MSG_TIMESTAMP = "Time since epoch\n{}"
MSG_IP = "{}"

NUM_MSG_STATES = 6

SCROLL_TIME = 5

LATEST_OBS_URL = "http://localhost/api/latest"

ERR_NO_POINTS = 0
ERR_SHOW_IP = 1
ERR_NO_ERROR = 2

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
        except KeyboardInterupt:
            pass
        finally:
            gpio.cleanup()

    def Setup(self):
        self._lcd = rgblcd(RSPIN, EPIN, D4PIN, D5PIN, D6PIN, D7PIN, LCD_COLUMNS, LCD_ROWS, RPIN, GPIN, BPIN)
        self._bltimeout = time.time() + BACKLIGHT_TIMEOUT
        self._lcdon = True
        self._laststate = 99
        self._state = 0
        self._error = ERR_SHOW_IP
        self._errAck = 0
        
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

        self._message = 0
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
            if self._state == 1:
                # Update messages with the lastest weather observation data point
                self.SetupMessages()

            # Add the Delta time for our slow loop
            self._slowtime += SLOW_LOOPDT
            
    def SetupMessages(self):
        '''
        0 - MSG_DEFAULT = "Temperature: {}" + DEGC + "\nHumidity: {}%"
        1 - MSG_TIME = "Today is:\n{}"
        2 - MSG_PRESSURE = "Pressure:\n{}hPa"
        3 - MSG_LUX = "Lux level:\n {}lx"
        4 - MSG_ALTITUDE = "Altitude: ()m"
        5 - MSG_TIMESTAMP = "Time since epoch\n{}"
        MSG_IP = "{}\n"
        '''
        self.GetLatest()
        if all (key in self._latest for key in ("temp", "rhum", "pres", "lux", "alt", "time")):
            self._msgDefault = MSG_DEFAULT.format(self._latest['temp'], self._latest['rhum'])
            self._msgTime = MSG_TIME.format(dt.today().strftime('%d-%m-%y : %H:%M'))
            self._msgPres = MSG_PRESSURE.format(self._latest['pres'])
            self._msgLux = MSG_LUX.format(self._latest['lux'])
            self._msgAlt = MSG_ALTITUDE.format(self._latest['alt'])
            self._msgTimestamp = MSG_TIMESTAMP.format(self._latest['time'])
        else:
            self._msgError = "Latest Points\nNot Found!"
            self._state = 0

    def DisplayMessage(self):
        self._lcd.clear()
        if self._message == 0:
            self._lcd.message(self._msgError)
        elif self._message == 1:
            self._lcd.message(self._msgDefault)
        elif self._message == 2:
            self._lcd.message(self._msgTime)
        elif self._message == 3:
            self._lcd.message(self._msgPres)
        elif self._message == 4:
            self._lcd.message(self._msgLux)
        elif self._message == 5:
            self._lcd.message(self._msgAlt)
        elif self._message == 6:
            self._lcd.message(self._msgTimestamp)
        else:
            self._lcd.message(self._msgIP)

    def ProcessState(self):
        if self._state == 0:
            if self._error == ERR_SHOW_IP:
                self._message = 99
            else:
                self._message = 0

            if self._errAck == 1:
                self._state = 1
                self._message = 1
                if self._error == ERR_NO_POINTS:
                    self.SetupMessages()
                elif self._error == ERR_SHOW_IP:
                    self._error = ERR_NO_ERROR

                self.errAck = 0
        elif self._state == 1:
            self._message = 1
        elif self._state == 2:
            self._message = 2
        elif self._state == 3:
            self._message = 3
        elif self._state == 4:
            self._message = 4
        elif self._state == 5:
            self._message = 5
        elif self._state == 6:
            self._message = 6
        elif self._state == 7:
            # If current screen has been displayed for
            # SCROLL_TIME swap to the next one
            if self._scrolltime < time.time():
                self._message += 1
                if self._message > NUM_MSG_STATES:
                    self._message = 1
                self._scrolltime += SCROLL_TIME
                self._laststate = 99
                self._bltimeout = time.time() + BACKLIGHT_TIMEOUT

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
            elif self._state == 7:
                self._state = 1
            else:
                # Process each key that has been pressed
                for key in self._keys:
                    print key
                    if key == KEY1PIN:
                        if self._state == 1:
                            self._state = NUM_MSG_STATES
                        else:
                            self._state -= 1
                    elif key == KEY2PIN:
                        if self._state == NUM_MSG_STATES:
                            self._state = 1
                        else:
                            self._state += 1
                    elif key == KEY3PIN:
                        self._state = 7
                        pass
                    elif key == KEY4PIN:
                        self._errAck = 1

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
