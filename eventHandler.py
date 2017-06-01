#!/usr/bin/python

import sys
import os
import pickle

outputFile = "/home/pi/alarm/output.txt"

os.remove(outputFile)

lines = sys.stdin.readlines()
varDict = {"action" : repr(sys.argv[1]).strip("'")}

for line in lines:
    if "=" in line:
        s = line.split("=")
        varDict[s[0].strip()] = s[1].strip()

with open(outputFile,"w") as f:
    #f.write("action=\"" + repr(sys.argv[1]).strip("'") + "\"\n")
    #for line in lines:
    #    if "=" in line:
    #        s = line.split("=")
    #        f.write(s[0].strip() + "=\"" + s[1].strip() + "\"\n")
    
    #f.write(sys.stdin.read())
    pickle.dump(varDict, f)
