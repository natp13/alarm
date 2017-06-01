#!/usr/bin/python

import time
import subprocess
import sys
import socket
from crontab import CronTab

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8888))

s.sendall("volume 100%\n")
data = s.recv(1024)
s.close()

# TODO: make this find the correct alarm instead of disabling all for now
root_cron = CronTab("root")
for job in root_cron:
    # CronItem job
    if job.command.match("startAlarmYoutube"):
        job.enable(False)

# write our changes back to the cron
root_cron.write()

videoUrl = "http://www.youtube.com/watch?v=fm660vIn8Tg"
if len(sys.argv) > 1:
    videoUrl = sys.argv[1]

command = "sudo -u pi cvlc --no-video -A alsa,none " + videoUrl + " --play-and-exit"
subprocess.call(command, shell=True)