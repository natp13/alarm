#!/usr/bin/python

import os
import sys
import time

#TODO: add argument validation
# scheduleWakeup.py hh mm am/pm

if len(sys.argv) != 4:
    print "invalid args"
    sys.exit()

hour = sys.argv[1]
min = sys.argv[2]

if sys.argv[3] == "pm":
    hour = repr(int(hour) + 12)

with open("/home/pi/alarm/alarmcron","w") as cronFile:
    cronFile.write(min + " " + hour + " * * * pianobar\n")
    cronFile.write(min + " " + hour + " * * * /home/pi/alarm/startAlarm.py\n")

os.system("crontab /home/pi/alarm/alarmcron")
