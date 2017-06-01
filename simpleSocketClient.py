#!/usr/bin/python

# simple python socket sender
import socket
import time

HOST = "localhost" # The remote host
PORT = 8888 # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print "Enter 'q' to quit"
command = ""
while (command != "q"):
    command = raw_input("alarmClock>> ")
    print command
    if command != "q":
        s.sendall(command + "\n")
        print (s.recv(1024))

s.close()