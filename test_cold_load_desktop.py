import os
import time
import sys

import signal
import subprocess

# A top-level script for running browsertime
#  For each site in sites.txt
#    For each set of defined preferences
#      Run browsertime

def cleanUrl(url):
    cleanUrl = url.replace("http://", '')
    cleanUrl = cleanUrl.replace("https://", '')
    cleanUrl = cleanUrl.replace("/", "|")
    cleanUrl = cleanUrl.replace(":", ";")
    cleanUrl = cleanUrl.replace('\n', ' ').replace('\r', '')
    return cleanUrl

# Configure the test here
firefox_binary_path = '--firefox.binaryPath="/Applications/Firefox Nightly.app/Contents/MacOS/firefox" '
iterations = '2'
# tuple of experiment name and firefox prefs
test_configs = [('baseline', ''), ('draw-fps', '--firefox.preference layers.acceleration.draw-fps:true' )]

preURL_config = '--preURL "http://www.example.com"  --preURLDelay 20000 '

file = open("sites.txt", "r")
for line in file:
  url = line.strip()
  prefs = test_configs
  for r, pref in enumerate(prefs):
      experimentName = pref[0]
      firefoxPrefs = pref[1]
      print(experimentName)
      print(firefoxPrefs)

      common_args = '-n ' + iterations + ' '

      resultUrl = cleanUrl(url)
      resultArg = '--resultDir "browsertime-results/' + resultUrl + '/' + experimentName + '" '

      completeCommand = './mach browsertime  --skipHar -vv ' + resultArg + firefoxPrefs + ' ' + firefox_binary_path + common_args + preURL_config +  url
      print( "\ncommand " + completeCommand)
      os.system(completeCommand)
