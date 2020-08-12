#!/usr/bin/env python3
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
# python process_vm.py {path}

# enable printing of debugging details
debug = False

class VariantResults:
  def __init__(self):
    self.means = []
    self.stdDevs = []
    self.relStdDevs = []
    self.medians = []
    self.meanSpeedups = []
    self.medianSpeedups = []
    
path = sys.argv[1]
os.chdir(path);
files = sorted(glob.glob("*"))

metrics = [['pageLoadTime', "data[0]['statistics']['timings']['pageTimings']", "['pageLoadTime']"],

          ['speedIndex', "data[0]['statistics']['visualMetrics']", "['SpeedIndex']"],
          ['contentfulSpeedIndex', "data[0]['statistics']['visualMetrics']", "['ContentfulSpeedIndex']"],
          ['perceptualSpeedIndex', "data[0]['statistics']['visualMetrics']", "['PerceptualSpeedIndex']"],
          ['visualComplete85', "data[0]['statistics']['visualMetrics']", "['VisualComplete85']"],
          ['firstVisualChange', "data[0]['statistics']['visualMetrics']", "['FirstVisualChange']"],
          ['lastVisualChange', "data[0]['statistics']['visualMetrics']", "['LastVisualChange']"],
          
          ['firstPaint', "data[0]['statistics']['timings']", "['firstPaint']"],
          ['timeToFirstInteractive', "data[0]['statistics']['timings']", "['timeToFirstInteractive']"],
          ['domInteractiveTime', "data[0]['statistics']['timings']['pageTimings']", "['domInteractiveTime']"],

          # ['redirectionTime', "data[0]['statistics']['timings']['pageTimings']", "['redirectionTime']"],
          # ['fetchStart', "data[0]['statistics']['timings']['navigationTiming']", "['fetchStart']"],
          # ['domainLookupStart', "data[0]['statistics']['timings']['navigationTiming']", "['domainLookupStart']"],
          # ['domainLookupEnd', "data[0]['statistics']['timings']['navigationTiming']", "['domainLookupEnd']"],
          # ['domainLookupTime', "data[0]['statistics']['timings']['pageTimings']", "['domainLookupTime']"],
          
          # ['connectStart', "data[0]['statistics']['timings']['navigationTiming']", "['connectStart']"],
          # ['serverConnectionTime', "data[0]['statistics']['timings']['pageTimings']", "['serverConnectionTime']"],

          # ['requestStart', "data[0]['statistics']['timings']['navigationTiming']", "['requestStart']"],
          # ['responseStart', "data[0]['statistics']['timings']['navigationTiming']", "['responseStart']"],
          # ['responseEnd', "data[0]['statistics']['timings']['navigationTiming']", "['responseEnd']"],
          
          # ['serverResponseTime', "data[0]['statistics']['timings']['pageTimings']", "['serverResponseTime']"],

          # ['domInteractiveTime', "data[0]['statistics']['timings']['pageTimings']", "['domInteractiveTime']"],

          # ['domContentLoadedTime', "data[0]['statistics']['timings']['pageTimings']", "['domContentLoadedTime']"],

          ['backEndTime', "data[0]['statistics']['timings']['pageTimings']", "['backEndTime']"],
          ['frontEndTime', "data[0]['statistics']['timings']['pageTimings']", "['frontEndTime']"],

          ['duration', "data[0]['statistics']['timings']['navigationTiming']", "['duration']"]
          ]


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
              data = json.load(f)

              instance = {}
              for metric in metrics:
                  if eval(metric[2])[0] not in eval(metric[1]):
                      instance[metric[0] + "Mean"] = 0
                      instance[metric[0] + "Stddev"] = 0
                      instance[metric[0] + "RelStddev"] = 0
                      instance[metric[0] + "Median"] = 0
                  else:
                      instance[metric[0] + "Mean"] = eval(metric[1] + metric[2] + "['mean']")
                      instance[metric[0] + "Stddev"] = eval(metric[1] + metric[2] + "['stddev']")
                      if float(instance[metric[0] + "Mean"]) == 0:
                        instance[metric[0] + "RelStddev"] = 0.0
                      else:
                        instance[metric[0] + "RelStddev"] = float(instance[metric[0] + "Stddev"]) / float(instance[metric[0] + "Mean"])
                      instance[metric[0] + "Median"] = eval(metric[1] + metric[2] + "['median']")
              instance['value']                              = session
              instance['timestamp']                          = data[0]['info']['timestamp']
              instance['url']                                = data[0]['info']['url']
              # instance['lcpContent']                         = data[0]['browserScripts'][0]['timings']['largestContentfulPaint']['url']
              # instance['lcpTagName']                         = data[0]['browserScripts'][0]['timings']['largestContentfulPaint']['tagName']
              instance['mode'] = session
              if debug: print( "report" )
              report.append(instance)

  sortedResults.append( sorted(report, key=itemgetter('timestamp'), reverse=False) )
  os.chdir("..")

numRows = 100

# Print data
speedups = []
variants = []

# For every site
for j,l in enumerate(sortedResults):

  print("%s:    |"% sortedResults[j][0]["url"], end="")

  #print every variant
  for i,instance in enumerate(sortedResults[0]):
    if debug: print("\nmetrics for " + instance['url'])
    if i == 0:
      print(instance['mode'] + " | | | ", end="")
    else:
      print(instance['mode'] + " | | | | | ", end="")

  print("")

  #print Mean, etc . headers
  for i,instance in enumerate(sortedResults[0]):
    if i == 0:
      print("| Mean | Rel Std Dev | Median | ", end="")
    else:
      print("Mean | Rel Std Dev | Improvement relative to baseline | Median | Improvement relative to baseline | ", end="")

  print("")

  # print every metric
  for metric in metrics:
    print(metric[0] + ":   |", end="")
    meanIndex = metric[0] + "Mean"
    medianIndex = metric[0] + "Median"
    stddevIndex = metric[0] + "Stddev"
    relstddevIndex = metric[0] + "RelStddev"

    baseValueMean = 0
    baseValueMedian = 0
    if debug:
      print("%s"% sortedResults[j][0]["url"], end="")
    #print("| ", end="")

    # print for every variant for a given site
    for i,instance in enumerate(sortedResults[j]):
      if i > 0 and instance['timestamp'] < sortedResults[j][i-1]['timestamp']:
        print("ERROR NOT SORTED!!")

      print("%4.0f"% instance[meanIndex]   + "|", end="")
      print("%4.4f"% instance[relstddevIndex] + "| ", end="")

      # Update variant values (i.e. columns)
      if len(variants) <= i: variants.append(VariantResults())

      if instance[meanIndex] != 0:
        variants[i].means.append(instance[meanIndex])
      if instance[stddevIndex] != 0:
        variants[i].stdDevs.append(instance[stddevIndex])
      if instance[relstddevIndex] != 0:
        variants[i].relStdDevs.append(instance[relstddevIndex])
      if instance[medianIndex] != 0:
        variants[i].medians.append(instance[medianIndex])          

      if i == 0:
        baseValueMean   = instance[meanIndex]
        baseValueMedian = instance[medianIndex]
      else:
        delta = (baseValueMean-instance[meanIndex])
        if baseValueMean != 0 and instance[meanIndex] != 0:
          speedup = (float(baseValueMean) - float(instance[meanIndex]))/float(baseValueMean)
          speedups.append( speedup )
        else:
          speedup = 0
          speedups.append(0)
        variants[i].meanSpeedups.append(speedup)
        print("%6.4f"% speedup + " | " , end="")

      print("   %4.0f"%  instance[medianIndex]   + " |  ", end="")
      
      if i == 0:
        print("", end="")
      else:
        if baseValueMedian != 0 and instance[medianIndex] != 0:
          speedup = (float(baseValueMedian) - float(instance[medianIndex]))/float(baseValueMedian)
        else:
          delta = 0
          speedup = 0
        variants[i].medianSpeedups.append(speedup)
        print("%6.4f"% speedup + "", end="")
        print(" |", end="")

    print("")
        
  print("")

  # print("Mean | ", end="")
  # for v,v2 in enumerate(variants):
  #   meanOfMeans = statistics.mean(variants[v].means) if len(variants[v].means) != 0 else 0.0 
  #   meanOfRelStdDevs = statistics.mean(variants[v].relStdDevs) if len(variants[v].relStdDevs) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMeans +  " | ", end="")
  #   print ("%4.4f"% meanOfRelStdDevs +  " | ", end="")
  #   if (v != 0):
  #     meanSpeedup = statistics.mean(variants[v].meanSpeedups) if len(variants[v].meanSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% meanSpeedup + " | ", end="")

  #   meanOfMedians = statistics.mean(variants[v].medians) if len(variants[v].medians) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMedians +  " | ", end="")
  #   if (v != 0):
  #     medianSpeedup = statistics.mean(variants[v].medianSpeedups) if len(variants[v].medianSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% medianSpeedup + " | ", end="")
  # print("")

  # print("Median | ", end="")
  # for v,v2 in enumerate(variants):
  #   meanOfMeans = statistics.median(variants[v].means) if len(variants[v].means) != 0 else 0.0 
  #   meanOfRelStdDevs = statistics.median(variants[v].relStdDevs) if len(variants[v].relStdDevs) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMeans +  " | ", end="")
  #   print ("%4.4f"% meanOfRelStdDevs +  " | ", end="")
  #   if (v != 0):
  #     meanSpeedup = statistics.median(variants[v].meanSpeedups) if len(variants[v].meanSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% meanSpeedup + " | ", end="")

  #   meanOfMedians = statistics.median(variants[v].medians) if len(variants[v].medians) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMedians +  " | ", end="")
  #   if (v != 0):
  #     medianSpeedup = statistics.median(variants[v].medianSpeedups) if len(variants[v].medianSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% medianSpeedup + " | ", end="")
  # print("")

  # # geomean can only be calculated on numbers > 0 (and there are some other constraints)
  # # values are in the range -N.0 (-N00%) to +1.0 (100%)
  # # remap -N% to be 0-1.0, and N% to be 1.0-M.   When outputting, subtract the 1.0
  # print("Geomean | ", end="")
  # for v,v2 in enumerate(variants):
  #   meanOfMeans = gmean(variants[v].means) if len(variants[v].means) != 0 else 0.0 
  #   meanOfRelStdDevs = gmean(variants[v].relStdDevs) if len(variants[v].relStdDevs) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMeans +  " | ", end="")
  #   print ("%4.4f"% meanOfRelStdDevs +  " | ", end="")
  #   if (v != 0):
  #     for l in range(len(variants[v].meanSpeedups)):
  #       variants[v].meanSpeedups[l] = (-variants[v].meanSpeedups[l]) + 1
  #     meanSpeedup = gmean(variants[v].meanSpeedups) if len(variants[v].meanSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% -(meanSpeedup-1) + " | ", end="")

  #   meanOfMedians = gmean(variants[v].medians) if len(variants[v].medians) != 0 else 0.0 
  #   print ("%4.2f"% meanOfMedians +  " | ", end="")
  #   if (v != 0):
  #     for l in range(len(variants[v].medianSpeedups)):
  #       variants[v].medianSpeedups[l] = (-variants[v].medianSpeedups[l]) + 1
  #     medianSpeedup = gmean(variants[v].medianSpeedups) if len(variants[v].medianSpeedups) != 0 else 0.0 
  #     print ("%4.4f"% -(medianSpeedup-1) + " | ", end="")


  print("")
  print("")