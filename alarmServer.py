#!/usr/bin/python

from pandoraStation import PandoraService
from youtubeStation import YoutubeStation
import time
import asyncore, asynchat, socket
import threading
import os
import sys
from collections import OrderedDict
import json
from crontab import CronTab

server = None
currentStation = None
initialStation = 13

# I think it makes sense for this to be static global since there is only one volume for the entire system
currentVolume = "80%"
def setSystemVolume(newVolume):
    # figure out why get_volume doesn't return the right volume
    # It was because you have to define that you want to use the global version of this variable.
    # I wonder why I don't have to do this for currentStation..? My guess is because it is an object not a primitive?
    global currentVolume
    currentVolume = newVolume
    os.system("amixer -c 0 -- sset PCM Playback " + newVolume)

class Station:
    HISTORY_LENGTH = 10

    # commands = {
        # "pause_play"    : station.pausePlay,
        # "stop"          : station.stop,
        # "song_info"     : station.getSongInfo,
        # "station"       : setStation,
        # "sleep"         : sleep,
        # "wakeup"        : wakeup,
        # "snooze"        : snooze
        # }    

    def __init__(self):
        self.station = None
        
        # End of list is most recently listened station
        self.stationHistory = OrderedDict([(str(initialStation), "")])
        
        self.stationDict = {}
    
    def _appendToStationHistory(self, station):
        if station in self.stationHistory:
            del self.stationHistory[station]
        elif len(self.stationHistory) > self.HISTORY_LENGTH:
            # remove the station at the beginning of the list cause this was the last one we listened to
            # del self.stationHistory[self.stationHistory.items()[0][0]] # there has got to be a better way to do this
            # and ... there it is:
            self.stationHistory.popitem(last=False)
        
        if station not in self.stationDict:
            try:
                self.stationDict = currentStation.get().getStations()
            except:
                pass

        if station in self.stationDict:
            #print station
            #print self.stationHistory
            #print "\n"
            #print self.stationDict[station]
            self.stationHistory[station] = self.stationDict[station]
        else:
            self.stationHistory[station] = ""

    def getStations(self):
        # TODO compile list of stations not just from pandora
        self.stationDict = currentStation.get().getStations()
        # stationList = []
        # for station in self.stationDict:
            # stationList.append({"id":station, "name":self.stationDict[station]})
        return self.stationDict
        
    def getStationHistory(self):
        return self.stationHistory.items()
        
    def get(self):
        return self.station
        
    def set(self, station):
        # TODO: need to destroy/pause the old station if there was one
        self.station = station
        
    def setStation(self, stationArgs):
        print stationArgs
        stationId = stationArgs[0].lower()
        if stationId == "youtube":
            # do youtube stuff
            print "opening youtube station: " + stationArgs[1]
            self.set(YoutubeStation(stationArgs[1]))
        else:
            self.set(PandoraService(stationId))

        self._appendToStationHistory(stationId)
        
    # def executeCommand(self, command, args):
        # self.commands[command](args)
        
    # def sleep(self, args):
        # return
    
    # def wakeup(self, args):
        # return
        
    # def setStation(self, args):
        # self.set(PandoraService(args[1]))

class SleepAlarm(threading.Thread):
    shouldSnooze = False
    station = 1

    def __init__(self, minutes, snooze = False, station = 1):
        threading.Thread.__init__(self)
        # TODO: parameter validation
        self.minutes = float(minutes)
        self.finished = threading.Event()
        self.shouldSnooze = snooze
        self.station = station
        
    def run(self):
        # TODO: handle can't connect to socket
        self.finished.wait(self.minutes * 60)
        #if not self.finished.is_set():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 8888))
        if (self.shouldSnooze):
            s.sendall("volume 100%\n")
            data = s.recv(1024)
            # s.sendall("play\n")
            s.sendall("station " + str(self.station) + "\n")
            data = s.recv(1024)
        else:
            s.sendall("stop\n")
            data = s.recv(1024)
        s.close()
        self.finished.set()

class WakeupAlarm():
    def __init__(self, cronjob):
        self.comment = cronjob.meta()
        self.job = cronjob
        try:
            self.station = str(self.job.command).split()[1]
        except:
            self.station = 13
        #self.minutes = int(str(self.job.minutes))
        #self.hours = int(str(self.job.hours))
        #self.ampm = "am"
        #if hoursInt > 12:
        #    self.hours = self.hours - 12
        #    self.ampm = "pm"

    def getDict(self):
        # return a dictionary of the alarm
        # hours: 1-12
        # minutes: 0-59
        # ampm: am/pm
        # enabled: True/False
        # station: ##
        alarmDict = {"minutes" : str(self.job.minutes), "enabled" : str(self.job.enabled), "station" : self.station}
        hoursInt = int(str(self.job.hours))
        if hoursInt > 12:
            alarmDict["hours"] = str(hoursInt - 12)
            alarmDict["ampm"] = "pm"
        else:
            alarmDict["hours"] = str(self.job.hours)
            alarmDict["ampm"] = "am"

        print alarmDict
        return alarmDict

    def setMinutes(self, minutes):
        self.job.minutes.on(minutes)

    def setHours24(self, hours):
        # note we put it in 24 hour clock here, but in getDict, we return the 12 hour clock
        self.job.hours.on(hours)

    def setStation(self, station):
        self.job.command = "/home/pi/alarm/startAlarm2.py " + str(station)

    def setEnabled(self, enabled):
        self.job.enable(enabled)

class AlarmConnectionHandler(asynchat.async_chat):
    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock=sock)
        self.set_terminator("\n")
        self.ibuffer = ""
        self.obuffer = ""
        
    # def __del__(self):
        # print "Destroying connection: \n"
        
    def collect_incoming_data(self, data):
        self.ibuffer += data
        
    def found_terminator(self):
        global server
        print self.ibuffer
        #commandArgs = [c.strip() for c in self.ibuffer.lower().strip().split()]
        commandArgs = [c.strip() for c in self.ibuffer.strip().split()]
        command = commandArgs[0].lower()
        
        # probably going to have to pass this string to musicService
        # so it can create a dictionary and pass the commands off itself
        # since there are going to be a bunch
        if command == "pause_play":
            self.send(currentStation.get().pausePlay())
        elif command == "stop":
            self.send(currentStation.get().stop())
        elif command == "play":
            self.send(currentStation.get().play())
        elif command == "next":
            currentStation.get().next()
        elif command == "song_info":
            info = currentStation.get().getSongInfo()
            #print "Artist: {0}\nTitle: {1}".format(info["artist"], info["title"])
            self.obuffer = json.dumps({"artist" : info["artist"], "title" : info["title"], "coverArt" : info["coverArt"]})
            #self.send("Artist: {0}    Title: {1}".format(info["artist"], info["title"]))
        elif command == "sleep":
            sleep = SleepAlarm(commandArgs[1])
            sleep.start()
        elif command == "station":
            #currentStation.set(PandoraService(commandArgs[1]))
            #currentStation.setStation(commandArgs[1])
            currentStation.setStation(commandArgs[1:])
        elif command == "wakeup":
            # args = [hour, min, am/pm, station]
            if len(commandArgs) < 5:
                print "invalid args for wakeup"
            hour = int(commandArgs[1])
            min = int(commandArgs[2])
            if commandArgs[3].lower() == "pm":
                hour = hour + 12
            # todo store wakeup and alarm states
            #with open("/home/pi/alarm/alarmcron","w") as cronFile:
            #    cronFile.write(min + " " + hour + " * * * /home/pi/alarm/startAlarm.py " + commandArgs[4] + "\n")

            #os.system("crontab /home/pi/alarm/alarmcron")
            server.wakeupAlarms[0].setHours24(hour)
            server.wakeupAlarms[0].setMinutes(min)
            server.wakeupAlarms[0].setStation(int(commandArgs[4]))

            if (len(commandArgs) > 5):
                server.wakeupAlarms[0].setEnabled(commandArgs[5].title() == "True")

            server.storeAlarms()
            server.reloadAlarms()
            
        elif command == "snooze":
            # args = [mins, station]
            self.obuffer = currentStation.get().stop()
            # Start a snooze alarm
            snooze = SleepAlarm(int(commandArgs[1]), True, commandArgs[2])
            snooze.start()
            self.obuffer += "...Snooze:" + commandArgs[1]

        elif command == "volume":
            setSystemVolume(commandArgs[1])
            self.obuffer = currentVolume[:-1]
            
        elif command == "stations":
            #self.send(currentStation.getStations())
            #self.push(currentStation.getStations())
            self.obuffer = json.dumps(currentStation.getStations())
            
        elif command == "station_history":
            self.obuffer = json.dumps(currentStation.getStationHistory())
            
        elif command == "get_volume":
            self.obuffer = currentVolume[:-1]

        elif command == "get_alarms":
            server.reloadAlarms()
            self.obuffer = json.dumps(server.getAlarms())

        elif command == "queue":
            try:
                self.obuffer = currentStation.get().queueSongUrl(commandArgs[1])
            except AttributeError:
                self.obuffer = "queue command not supported for current station"

        elif command == "loop":
            try:
                self.obuffer = currentStation.get().toggleLoop()
            except AttributeError:
                self.obuffer = "loop command not supported for current station"

        else:
            print "unknown command"
            #self.send("unknown command")
            self.obuffer = "unknown command"
            
        #self.send("\n")
        self.obuffer += "\n"
        self.push(self.obuffer)
            
        #reset the buffer (is this even necessary? I think not)
        self.ibuffer = ""
        self.obuffer = ""

        # note we shouldn't do this because we want to allow the connection
        # to stay open for clients who want to send multiple commands (alarms)
        # self.close_when_done()
            
    def handle_close(self):
        # print "closing"
        self.close()

class AlarmServer(asyncore.dispatcher):
    def __init__(self, host, port):
        self.wakeupAlarms = []
        self.root_cron = CronTab("root")
        self.reloadAlarms()

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print "Incoming connection {}".format(repr(addr))
            handler = AlarmConnectionHandler(sock)

    def reloadAlarms(self):
        self.wakeupAlarms = [] # list of WakeupAlarms
        self.root_cron = CronTab("root")
        for job in self.root_cron:
            # CronItem job
            if job.command.match("startAlarm"):
                self.wakeupAlarms.append(WakeupAlarm(job))

    def getAlarms(self):
        alarms = []
        for alarm in self.wakeupAlarms:
            alarms.append(alarm.getDict())

        return alarms

    def storeAlarms(self):
        self.root_cron.write()

if __name__=="__main__":
    beginPlaying = 1

    if (len(sys.argv) > 1):
        # first argument should be the station
        initialStation = int(sys.argv[1])
    
    if (len(sys.argv) > 2):
        # second argument is 1 if we should immediately start playing
        # 0 otherwise
        beginPlaying = int(sys.argv[2])
        
    if beginPlaying:
        setSystemVolume("80%")
    else:
        setSystemVolume("0%")

    # this happens in AlarmServer.initializeState
    # load the alarms
    #root_cron = CronTab("root")
    #alarmJobs = root_cron.find_command("startAlarm")
    #for job in alarmJobs:
        
    # create the pandora service and begin playing music
    currentStation = Station()
    currentStation.set(PandoraService(initialStation))
    
    if not beginPlaying:
        time.sleep(20)
        currentStation.get().stop()
        setSystemVolume(currentVolume)

    server = AlarmServer("localhost", 8888)
    asyncore.loop()
    
    # while(1):
        # time.sleep(20)
        # pandora.pausePlay()