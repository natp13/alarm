#!/usr/bin/python

#import threading
import subprocess
import time

ctlPipe = "/home/pi/alarm/youtubeCtl"

class YoutubeStation:
    musicPlaying = False
    loopEnabled = False

    def __init__(self, url):
        # note need to keep the control fifo pipe open until object destroyed
        # then open it again to process commands.
        # but it can't be opened until after the call to start the vlc process

        print "checking processes for vlc"
        # open a new subprocess for running the vlc player if it's not already running
        procs = subprocess.check_output(["ps", "-A"])

        if "vlc" not in procs:
            print "starting vlc"
            # get input from youtubeCtl fifo pipe and output everything into the abyss
            subprocess.call("sudo -u pi vlc --no-video -A alsa,none </home/pi/alarm/youtubeCtl >/home/pi/alarm/vlcOutput.txt 2>&1 &", shell=True)
        else:
            print "vlc already exists"
            self.clearPlaylist()

        print "opening youtube control pipe"
        self.controlPipeFile = open(ctlPipe, "w")

        #time.sleep(15)
        self.addSongUrl(url)
        print "done initializing youtube station"

    def __del__(self):
        try:
            self.controlPipeFile.close()
            print "closed control pipe"
        except:
            print "youtube control pipe already closed..."

    # TODO: add vlc commands here

    def sendCommand(self, command):
        """ Send a command to vlc through the control fifo pipe"""
        with open(ctlPipe, "w") as f:
            f.write(command + "\n")

    def clearPlaylist(self):
        """ Clear the current playlist """
        self.sendCommand("clear")

    def pausePlay(self):
        """ Toggles pause/play """
        self.sendCommand("pause")
        self.musicPlaying = not self.musicPlaying
        if self.musicPlaying:
            return "playing"
        else:
            return "paused"

    def stop(self):
        if self.musicPlaying:
            self.sendCommand("pause")
            self.musicPlaying = False
        return "stopped"
        
    def play(self):
        if not self.musicPlaying:
            self.sendCommand("pause")
            self.musicPlaying = True
        return "playing"

    def next(self):
        self.sendCommand("next")

    def addSongUrl(self, url):
        print "adding song url " + url
        self.sendCommand("add " + url)
        self.musicPlaying = True

    def queueSongUrl(self, url):
        self.sendCommand("enqueue " + url)
        return "queued: " + url

    def toggleLoop(self):
        self.loopEnabled = not self.loopEnabled
        loopArg = "on" if self.loopEnabled else "off"
        print "loop " + loopArg
        self.sendCommand("loop " + loopArg)
        return str("Loop " + loopArg)

#class VlcPlayer(threading.thread):
#    pass