#!/usr/bin/python3
from __future__ import print_function

import json
import os.path
import glob
import math
import statistics
import numpy as np
from shutil import copyfile
from operator import itemgetter
import fnmatch
import os

def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod()**(1.0/len(a))

os.chdir("browsertime-results");
files = glob.glob("*")

metrics = ['pageLoadTime', 'responseStart', 'firstPaint','firstContentfulPaint']

sortedResults = []
for url in files:
  os.chdir(url)
  print("\nProcessing " + url)

  report = []
  sessions = glob.glob("*")
  for k,session in enumerate(sessions):

      matches = []
      for root, dirnames, filenames in os.walk(session):
        print("\root " + root)
        for filename in fnmatch.filter(filenames, 'browsertime.json'):
            print("\nfilename " + filename)
            matches.append(os.path.join(root, filename))

      if not matches:
        continue
      #results = glob.glob("session/**/browsertime.json", recursive=True)

      for r, result in enumerate(matches):
          print("\nOpening " + result)
          with open(result) as f:
          #with open(session + "/browsertime.json") as f:
              data = json.load(f)

              responseStartMean   = data[0]['statistics']['timings']['pageTimings']['backEndTime']['mean']
              responseStartStddev = data[0]['statistics']['timings']['pageTimings']['backEndTime']['stddev']
              responseStartMedian = data[0]['statistics']['timings']['pageTimings']['backEndTime']['median']

              pageLoadMean   = data[0]['statistics']['timings']['pageTimings']['pageLoadTime']['mean']
              pageLoadStddev = data[0]['statistics']['timings']['pageTimings']['pageLoadTime']['stddev']
              pageLoadMedian = data[0]['statistics']['timings']['pageTimings']['pageLoadTime']['median']

              firstPaintMean   = data[0]['statistics']['timings']['firstPaint']['mean']
              firstPaintStddev = data[0]['statistics']['timings']['firstPaint']['stddev']
              firstPaintMedian = data[0]['statistics']['timings']['firstPaint']['median']

              if 'timeToContentfulPaint' not in data[0]['statistics']['timings']:
                firstContentfulPaintMean   = 0
                firstContentfulPaintStddev = 0
                firstContentfulPaintMedian = 0
              else:
                firstContentfulPaintMean   = data[0]['statistics']['timings']['timeToContentfulPaint']['mean']
                firstContentfulPaintStddev = data[0]['statistics']['timings']['timeToContentfulPaint']['stddev']
                firstContentfulPaintMedian = data[0]['statistics']['timings']['timeToContentfulPaint']['median']
              
              instance = {}
              instance['responseStartMean']              = responseStartMean
              instance['responseStartStddev']                = responseStartStddev
              instance['responseStartMedian']                = responseStartMedian
              instance['pageLoadTimeMean']                   = pageLoadMean
              instance['pageLoadTimeStddev']                 = pageLoadStddev
              instance['pageLoadTimeMedian']                 = pageLoadMedian
              instance['firstPaintMean']                     = firstPaintMean
              instance['firstPaintStddev']                   = firstPaintStddev
              instance['firstPaintMedian']                   = firstPaintMedian
              instance['firstContentfulPaintMean']           = firstContentfulPaintMean
              instance['firstContentfulPaintStddev']         = firstContentfulPaintStddev
              instance['firstContentfulPaintMedian']         = firstContentfulPaintMedian
              instance['value']                              = session
              instance['timestamp']                          = data[0]['info']['timestamp']
              instance['url']                                = data[0]['info']['url']
              report.append(instance)

  sortedResults.append( sorted(report, key=itemgetter('timestamp')) )
  os.chdir("..")

numRows = 100

print("\n")
# Print data
speedups = []
for metric in metrics:
  print(metric + ":")
  print("-"*numRows)
  for j,l in enumerate(sortedResults):
    meanIndex = metric + "Mean"
    medianIndex = metric + "Median"
    stddevIndex = metric + "Stddev"
    baseValueMean = 0
    baseValueMedian = 0
    print("%-30.30s"% sortedResults[j][0]["url"], end="")
    print("| ", end="")
    for i,instance in enumerate(sortedResults[j]):
      if i > 0 and instance['timestamp'] < sortedResults[j][i-1]['timestamp']:
        print("ERROR NOT SORTED!!")

      print("%9.2f"%  instance[meanIndex]   + " ", end="")
      print("(+-%4.0f"% instance[stddevIndex] + ") ", end="")
      
      if i == 0:
        baseValueMean   = instance[meanIndex]
        baseValueMedian = instance[medianIndex]
      else:
        delta = (baseValueMean-instance[meanIndex])
        speedup = delta/float(baseValueMean)*100.0
        speedups.append( baseValueMean/instance[meanIndex] )
        print("%6.2f"% speedup + "%", end="")
    
      print("   %9.2f"%  instance[medianIndex]   + " ", end="")
    
      if i == 0:
        #print(" "*5, end="")
        print("|", end="")
      else:
        delta = (baseValueMedian-instance[medianIndex])
        speedup = delta/float(baseValueMedian)*100.0
        print("%6.2f"% speedup + "%", end="")
        print(" |", end="")


    print("")
  print("-"*numRows)
  #print("Geomean: " + "%6.4f"% geo_mean(speedups) + "\n")
