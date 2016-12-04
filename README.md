# weatherstation
Home weather station web interface

Dual raspberry pi setup with external pi pushing data points to the API endpoint running on a second raspberry pi inside.
Internal raspberry pi runs a Bottle.py API and a Vue.js front end. Also provides latest point data via a 16x2 RGB LCD.

Future Plans:
Add graph representations of the data.
Add support for Wind Direction and Speed
Add support for Rainfall

Daemon.py from: http://web.archive.org/web/20131017130434/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
