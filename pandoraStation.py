#!/usr/bin/python

#import os
#import sys
#import time
import subprocess
import pickle

remote = "/home/pi/.config/pianobar/ctl"
songInfoFile = "/home/pi/alarm/output.txt"

# TODO: make this thread safe
# TODO: should I check for the process on every command?
# yes because otherwise the write calls will be blocking

class PandoraService:
    stationSelected = False
    musicPlaying = False
    
    def __init__(self, station):
        station = str(station)
        # see if pianobar is already running
        procs = subprocess.check_output(["ps", "-A"])
        
        if "pianobar" not in procs:
            # we need to start pianobar
            # and then once it starts, pause it immediately
            self.stationSelected = False
            # route in and out to /dev/null and route stderr to stdout (/dev/null)
            player = subprocess.call("sudo -u pi pianobar >/dev/null </dev/null 2>&1 &", shell=True)
            #self.sendCommand(station + "\n")
            self.stationSelected = True
        # else:
            # It's already running so just change the station
            # This will even work if we are already on this station because it will 
            # just restart the music.
        self.sendCommand("s" + station + "\n")
        
        self.musicPlaying = True
                
    def sendCommand(self, command):
        with open(remote,"w") as f:
            f.write(command)
            
    def pausePlay(self):
        self.sendCommand("p")
        self.musicPlaying = not self.musicPlaying
        if self.musicPlaying:
            return "playing"
        else:
            return "paused"
        
    def stop(self):
        if self.musicPlaying:
            self.sendCommand("p")
            self.musicPlaying = False
            
        return "stopped"
        
    def play(self):
        if not self.musicPlaying:
            self.sendCommand("p")
            self.musicPlaying = True
            
        return "playing"
        
    def next(self):
        self.sendCommand("n")
        
    def getSongInfo(self):
        with open(songInfoFile,"r") as f:
            data = pickle.load(f)
            
        return data
        
    def getStations(self):
        with open(songInfoFile,"r") as f:
            data = pickle.load(f)
            
        stations = {}
        for info in data:
            if (info[:7] == "station") and (info[7:] != "Count") and (info[7:] != "Name"):
                stations[info[7:]] = data[info]
                
        return stations