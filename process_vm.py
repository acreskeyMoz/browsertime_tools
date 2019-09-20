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
from scipy.stats.mstats import gmean

# process usage: supply the path of the top-level browsertime-results directory
# python ./process.py {path}

# enable printing of debugging details
debug = False

class VariantResults:
  def __init__(self):
    self.means = []
    self.stdDevs = []
    self.medians = []
    self.meanSpeedups = []
    self.medianSpeedups = []

def filter_outliers(loads, threshold):
  length = len(loads)
  median = statistics.median(loads)
  mean   = statistics.mean(loads)
  stdev  = statistics.stdev(loads)

  ratio = stdev/mean
  while ratio > threshold:
    maxDiff = 0
    maxIndex = 0
    for i,val in enumerate(loads):
      if abs(val-median) > maxDiff:
        maxDiff = abs(val-median)
        maxIndex = i

    #print("Removing index " + str(maxIndex) + " with value " + str(loads[maxIndex]))
    del loads[maxIndex]
    if len(loads) <= 5:
      return

    mean = statistics.mean(loads)
    median = statistics.median(loads)
    ratio = statistics.stdev(loads)/mean
    
path = sys.argv[1]
os.chdir(path);
files = sorted(glob.glob("*"))

metrics = [['pageLoadTime', "data[0]['statistics']['timings']['pageTimings']", "['pageLoadTime']"],
          ['speedIndex', "data[0]['statistics']['visualMetrics']", "['SpeedIndex']"],
          ['contentfulSpeedIndex', "data[0]['statistics']['visualMetrics']", "['ContentfulSpeedIndex']"],
          ['responseStart', "data[0]['statistics']['timings']['pageTimings']", "['backEndTime']"],
          ['firstPaint', "data[0]['statistics']['timings']", "['firstPaint']"],
          # Not at this position in Chrome ['firstContentfulPaint', "data[0]['statistics']['timings']", "['timeToContentfulPaint']"],
          # https://github.com/mozilla/browsertime/issues/39
          ['visualComplete85', "data[0]['statistics']['visualMetrics']", "['VisualComplete85']"],
          ['perceptualSpeedIndex', "data[0]['statistics']['visualMetrics']", "['PerceptualSpeedIndex']"]]

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
          if debug: print("\nOpening " + result)
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
  meanIndex = metric[0] + "Mean"
  medianIndex = metric[0] + "Median"
  stddevIndex = metric[0] + "Stddev"

  print(metric[0] + ":   |", end="")
  for i,instance in enumerate(sortedResults[0]):
    if i == 0:
      print(instance['mode'] + " | | | ", end="")
    else:
      print(instance['mode'] + " | | | | | ", end="")

  print(" | ")

  for i,instance in enumerate(sortedResults[0]):
    if i == 0:
      print("| Mean | Std Dev | Median | ", end="")
    else:
      print("Mean | Std Dev | Mean speed relative to baseline | Median | Median peed relative to baseline | ", end="")

  print("")
  #print("-"*numRows)

  variants = []
  for j,l in enumerate(sortedResults):
    baseValueMean = 0
    baseValueMedian = 0
    print("%-50.50s"% sortedResults[j][0]["url"], end="")
    print("| ", end="")
    for i,instance in enumerate(sortedResults[j]):
      if i > 0 and instance['timestamp'] < sortedResults[j][i-1]['timestamp']:
        print("ERROR NOT SORTED!!")

      print("%4.0f"% instance[meanIndex]   + "|", end="")
      print("%4.0f"% instance[stddevIndex] + "| ", end="")
     
      # Update variant values (i.e. columns)
      if len(variants) <= i: variants.append(VariantResults())

      variants[i].means.append(instance[meanIndex])
      variants[i].stdDevs.append(instance[stddevIndex])
      variants[i].medians.append(instance[medianIndex])          
      #print ("variant: " + str(i) + " added: " + str(instance[meanIndex]))
      #print ("variant array: " + str(variants[i].means))

      if i == 0:
        baseValueMean   = instance[meanIndex]
        baseValueMedian = instance[medianIndex]
      else:
        delta = (baseValueMean-instance[meanIndex])
        if baseValueMean != 0 and instance[meanIndex] != 0:
          #speedup = delta/float(baseValueMean)*100.0
          speedup = float(baseValueMean)/float(instance[meanIndex])
          speedups.append( baseValueMean/instance[meanIndex] )
        else:
          speedup = 0
          speedups.append(0)
        variants[i].meanSpeedups.append(speedup)
        print("%6.2f"% speedup + " | " , end="")

      print("   %4.0f"%  instance[medianIndex]   + " |  ", end="")
      
      if i == 0:
        #print(" "*5, end="")
        print("", end="")
      else:
        if baseValueMedian != 0:
          delta = (baseValueMedian-instance[medianIndex])
          #speedup = delta/float(baseValueMedian)*100.0
          speedup = float(baseValueMedian)/float(instance[medianIndex])
        else:
          delta = 0
          speedup = 0
        variants[i].medianSpeedups.append(speedup)
        print("%6.2f"% speedup + "", end="")
        print(" |", end="")

    print("")

  print("Geomean | ", end="")
  for v,v2 in enumerate(variants):
    print ("%4.0f"% gmean(variants[v].means) +  " | ", end="")
    print ("%4.0f"% gmean(variants[v].stdDevs) +  " | ", end="")
    if (v != 0): print ("%4.2f"% gmean(variants[v].meanSpeedups) +  " | ", end="")
    print ("%4.0f"% gmean(variants[v].medians) +  " | ", end="")
    if (v != 0): print ("%4.2f"% gmean(variants[v].medianSpeedups) +  " | ", end="")
  print("")
  print("")
  #print("-"*numRows)
