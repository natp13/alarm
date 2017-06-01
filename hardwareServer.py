#!/usr/bin/python

# Note, this must be run as admin to import this
import RPi.GPIO as GPIO
import socket

PAUSE_PLAY_PIN = 17

def buttonPress(channel):
    if (channel == PAUSE_PLAY_PIN):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 8888))
        s.sendall("pause_play\n")
        response = s.recv(1024)
        s.close()
        
try:
    GPIO.setmode(GPIO.BCM)
    # Setup pin for input
    GPIO.setup(PAUSE_PLAY_PIN, GPIO.IN)

    # This would be true, except the switch is backwards...
    # When switch isn't pressed, the reading should be a 1, since I'm using pullup resistor
    # By specifying rising
    # 200ms bounce time for debounce
    GPIO.add_event_detect(17, GPIO.FALLING, callback=buttonPress, bouncetime=200)
    #GPIO.add_event_callback(17, buttonPress)

    # let us run forever
    while(1):
        pass
    
finally:
    GPIO.cleanup()