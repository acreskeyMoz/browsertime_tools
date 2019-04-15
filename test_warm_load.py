import os
import time

# A top-level script for generating warm load data from browsertime
#  For each site in sites.txt
#    For each set of defined preferences
#      Run the one.sh script, passing in reload parameters
file = open("sites.txt", "r")
for url in file:

  command = 'env ANDROID_SERIAL=ZY322HN4DN bash one.sh -n 1 --browsertime.reloads 30 -vv '

  # Define the preferences that each variant will use in this array of strings
  prefs = ['','--firefox.preference network.http.rcwn.enabled:false','--firefox.preference browser.cache.memory.capacity:-1', '--firefox.preference network.http.rcwn.enabled:false --firefox.preference browser.cache.memory.capacity:-1']
  for r, pref in enumerate(prefs):
      print( pref )
      print( "\nrestart adb")
      os.system("adb kill-server")
      os.system("adb devices")
      
      os.system('sleep 2')
      completeCommand = command + pref + ' reload.js' + ' --browsertime.url ' + url

      print( "\ncommand" + completeCommand)
      os.system(completeCommand)
