#!/usr/bin/python

import time
import os
import sys
import socket
from crontab import CronTab

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8888))

s.sendall("volume 100%\n")
data = s.recv(1024)

s.sendall("station " + sys.argv[1] + "\n")
data = s.recv(1024)

# TODO: make this find the correct alarm instead of disabling all for now
root_cron = CronTab("root")
for job in root_cron:
    # CronItem job
    if job.command.match("startAlarm"):
        job.enable(False)

# write our changes back to the cron
root_cron.write()

# let the alarm go for 10 minutes before turning it off
# except not any more since we have a snooze feature now
# time.sleep(60*10)

# with open("/home/pi/.config/pianobar/ctl","w") as fifoPipe:
    # fifoPipe.write("q")

# s.sendall("stop\n")
# data = s.recv(1024)

s.close()

# note that this removes all of the cronjobs, so I should try to be smarter
# about this in the future
#os.system("crontab -r")
