#!/usr/bin/env python
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from itertools import repeat
import subprocess
import glob
lightshows = glob.glob('/etc/hatchan/scripts/lights/*.py')
import psutil
import os
lightlisti = 0
def startProcess(name, path):
    # Start process
    process = subprocess.Popen(path, shell=False)

    # Write PID file
    pidfilename = os.path.join("/tmp/", name + '.pid')
    pidfile = open(pidfilename, 'w')
    pidfile.write(str(process.pid))
    pidfile.close()

    return process.pid
def savecounter():
    p = psutil.Process(stripprog)
    p.terminate()

import atexit
atexit.register(savecounter)

while True:
	  print len(lightshows)
          if len(lightshows) == lightlisti:
           lightlisti = 0
	  print lightlisti
	  if lightshows[lightlisti] == "/etc/hatchan/scripts/lights/fulldemo.py":
	   lightlisti += 1
          if len(lightshows) == lightlisti:
           lightlisti = 0
	  print lightshows[lightlisti]
          stripprog = startProcess("strip2", lightshows[lightlisti])
	  time.sleep(25)
          p = psutil.Process(stripprog)
          p.terminate()
	  lightlisti += 1

