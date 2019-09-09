#!/usr/bin/python3
from __future__ import print_function

import fnmatch
import glob
import json
import math
import numpy as np
import os
import statistics
import sys
from shutil import copyfile
from operator import itemgetter

# process usage: supply the path of the top-level browsertime-results directory
# python ./process.py {path}

# enable printing of debugging details
debug = False

def geo_mean(iterable):
  a = np.array(iterable)
  return a.prod()**(1.0/len(a))

path = sys.argv[1]
os.chdir(path);
files = sorted(glob.glob("*"))

metrics = [['pageLoadTime', "data[0]['statistics']['timings']['pageTimings']", "['pageLoadTime']"],
          ['responseStart', "data[0]['statistics']['timings']['pageTimings']", "['backEndTime']"],
          ['firstPaint', "data[0]['statistics']['timings']", "['firstPaint']"],
          ['firstContentfulPaint', "data[0]['statistics']['timings']", "['timeToContentfulPaint']"],
          ['visualComplete85', "data[0]['statistics']['visualMetrics']", "['VisualComplete85']"],
          ['speedIndex', "data[0]['statistics']['visualMetrics']", "['SpeedIndex']"],
          ['perceptualSpeedIndex', "data[0]['statistics']['visualMetrics']", "['PerceptualSpeedIndex']"],
          ['contentfulSpeedIndex', "data[0]['statistics']['visualMetrics']", "['ContentfulSpeedIndex']"]]

sortedResults = []
for url in files:
  os.chdir(url)
  if debug: print("\nProcessing " + url)

  report = []
  sessions = glob.glob("*")
  for k,session in enumerate(sessions):
      if debug: print("Session: " + session)
      matches = []
      for root, dirnames, filenames in os.walk(session):
        for filename in fnmatch.filter(filenames, 'browsertime.json'):
            if debug: print("\nfilename " + filename)
            matches.append(os.path.join(root, filename))

      if not matches:
        continue

      for r, result in enumerate(matches):
          #print("\nOpening " + result)
          with open(result) as f:
          #with open(session + "/browsertime.json") as f:
              data = json.load(f)

              instance = {}
              for metric in metrics:
                  if eval(metric[2])[0] not in eval(metric[1]):
                      instance[metric[0] + "Mean"] = 0
                      instance[metric[0] + "Stddev"] = 0
                      instance[metric[0] + "Median"] = 0
                  else:
                      instance[metric[0] + "Mean"] = eval(metric[1] + metric[2] + "['mean']")
                      instance[metric[0] + "Stddev"] = eval(metric[1] + metric[2] + "['stddev']")
                      instance[metric[0] + "Median"] = eval(metric[1] + metric[2] + "['median']")
              instance['value']                              = session
              instance['timestamp']                          = data[0]['info']['timestamp']
              instance['url']                                = data[0]['info']['url']
              instance['mode'] = session
              report.append(instance)

  sortedResults.append( sorted(report, key=itemgetter('timestamp')) )
  os.chdir("..")

numRows = 100
print("\n")

# Print data
speedups = []
for metric in metrics:
  print(metric[0] + ":   |", end="")
  for i,instance in enumerate(sortedResults[0]):
    if i == 0:
      print(instance['mode'] + " | | ", end="")
    else:
      print(instance['mode'] + " | | | | ", end="")

  print("             | ")

  for i,instance in enumerate(sortedResults[0]):
    if i == 0:
      print("| Mean | Median | ", end="")
    else:
      print("Mean | speedup | Median | speedup | ", end="")

  print("")
  print("-"*numRows)
  for j,l in enumerate(sortedResults):
    meanIndex = metric[0] + "Mean"
    medianIndex = metric[0] + "Median"
    stddevIndex = metric[0] + "Stddev"
    baseValueMean = 0
    baseValueMedian = 0
    print("%-30.30s"% sortedResults[j][0]["url"], end="")
    print("| ", end="")
    for i,instance in enumerate(sortedResults[j]):
      if i > 0 and instance['timestamp'] < sortedResults[j][i-1]['timestamp']:
        print("ERROR NOT SORTED!!")

      print("%9.2f"%  instance[meanIndex]   + " ", end="")
      print("(+-%4.0f"% instance[stddevIndex] + ") | ", end="")

      if i == 0:
        baseValueMean   = instance[meanIndex]
        baseValueMedian = instance[medianIndex]
      else:
        delta = (baseValueMean-instance[meanIndex])
        if baseValueMean != 0 and instance[meanIndex] != 0:
          speedup = delta/float(baseValueMean)*100.0
          speedups.append( baseValueMean/instance[meanIndex] )
        else:
          speedup = 0
          speedups.append(0)
        print("%6.2f"% speedup + "% | " , end="")

      print("   %9.2f"%  instance[medianIndex]   + " |  ", end="")

      if i == 0:
        #print(" "*5, end="")
        print("", end="")
      else:
        if baseValueMedian != 0:
          delta = (baseValueMedian-instance[medianIndex])
          speedup = delta/float(baseValueMedian)*100.0
        else:
          delta = 0
          speedup = 0
        print("%6.2f"% speedup + "%", end="")
        print(" |", end="")


    print("")
  print("-"*numRows)
#print("Geomean: " + "%6.4f"% geo_mean(speedups) + "\n")