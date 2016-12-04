#!/usr/bin/env python

from Adafruit_CharLCD import Adafruit_RGBCharLCD as rgblcd 
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
        self.lcd = rgblcd(RSPIN, EPIN, D4PIN, D5PIN, D6PIN, D7PIN, LCD_COLUMNS, LCD_ROWS, RPIN, GPIN, BPIN)
        self.bltimeout = time.time()
        self.state = 0xb00000001
        
        self.latest = {}

        # loop vars
        self.slowtime = time.time()
        self.fasttime = time.time()

    def Loop(self):
        # Fast loop
        if self.fasttime >= time.time():

            # Add the Delta time for our fast loop
            self.fasttime += FAST_LOOPDT

        # Slow loop
        if self.slowtime >= time.time():
            if self.state == 0:
                # Update messages with the lastest weather observation data point
                self.setMessage(self.GetLatest())


            # Add the Delta time for our slow loop
            self.slowtime += SLOW_LOOPDT
            

    def SetupMessages(self, obsPoint):
        self.lastMessage = self.message
        self.message = line1 + "\n" + line2
        

    def GetLatest(self):
        r = requests.get("http://localhost/api/latest")

        if r.status_code == 200:
            return True, r.json() 
        else:
            return False, "API returned\nStatus code {}".format(r.status_code)


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
