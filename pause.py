#!/usr/bin/python

import time
import sys
import socket

def secs(s):
    try:
        return float(s)*60
    except ValueError:
        return -1

if (__name__=="__main__"):

    print sys.argv

    if (len(sys.argv) != 2):
        print "Must enter the number of minutes to sleep!"
        sys.exit()
    elif (secs(sys.argv[1]) < 0):
	print sys.argv[1] + " is not a correct sleep time in minutes!"
        sys.exit()

    time.sleep(secs(sys.argv[1]))
    # with open("/home/pi/.config/pianobar/ctl","w") as fifoPipe:
        # fifoPipe.write("p")
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8888))
    s.sendall("pause_play\n")
    s.close()
