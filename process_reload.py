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


# This script transforms a folder of browsertime "warm load" results
#  into a table sent to standard output
# Steps:
# - scan the browsertime results for json files
# - collect the relevant page timing metrics
# - print them in a table, adding means, medians


def get_reload_values(data, url, metric, variantIndex):
    reloads = []
    for i,site in enumerate(data):
      if site['url'] == url:
        for j,load in enumerate(site['loads']):
          #ignore first load (cold)
          if j > 0:
            reloads.append(load[variantIndex][metric])

    return reloads

def get_reload_mean(data, url, metric, variantIndex):
    reloads = get_reload_values(data, url, metric, variantIndex)
    a = np.array(reloads)
    if len(a) == 0:
      return 0
    else:
      return a.mean()

def get_reload_stddev(data, url, metric, variantIndex):
    reloads = get_reload_values(data, url, metric, variantIndex)
    a = np.array(reloads)
    if len(a) == 0:
      return 0
    else:
      return a.std()

def get_reload_median(data, url, metric, variantIndex):
    reloads = get_reload_values(data, url, metric, variantIndex)
    a = np.array(reloads)
    if len(a) == 0:
      return 0
    else:
      return np.median(a)

def get_json_timestamp(filename):
    timestamp = ""
    with open(filename) as filehandle:
      data = json.load(filehandle)
      timestamp = data[0]['info']['timestamp']
    return timestamp

# find and collect results
os.chdir("browsertime-results");
urls = glob.glob("*")

metrics = ['pageLoadTime', 'responseStart', 'firstPaint','firstContentfulPaint']

sortedResults = []
results = []

for url in urls:
  os.chdir(url)
  
  # For each top-level url
  print("\nProcessing " + url)

  report = []
  
  urlData = {}
  urlData['url'] = url
  urlData['loads'] = []

  # find all the browsertime.json's for this url
  matches = []
  for root, dirnames, filenames in os.walk("."):
    for filename in fnmatch.filter(filenames, 'browsertime.json'):
      matches.append(os.path.join(root, filename))

  # sort the results by the browsertime timestamp
  sortedMatches = sorted(matches, key=get_json_timestamp)

  # for each json file
  for r, result in enumerate(sortedMatches):
    print("Opening " + result)
    with open(result) as f:
      data = json.load(f)

      #for each load
      loadNum = 0
      for load in data:
        responseStartMean   = load['statistics']['timings']['pageTimings']['backEndTime']['mean']
        responseStartStddev = load['statistics']['timings']['pageTimings']['backEndTime']['stddev']
        responseStartMedian = load['statistics']['timings']['pageTimings']['backEndTime']['median']

        pageLoadMean   = load['statistics']['timings']['pageTimings']['pageLoadTime']['mean']
        pageLoadStddev = load['statistics']['timings']['pageTimings']['pageLoadTime']['stddev']
        pageLoadMedian = load['statistics']['timings']['pageTimings']['pageLoadTime']['median']

        firstPaintMean   = load['statistics']['timings']['firstPaint']['mean']
        firstPaintStddev = load['statistics']['timings']['firstPaint']['stddev']
        firstPaintMedian = load['statistics']['timings']['firstPaint']['median']

        if 'timeToContentfulPaint' not in load['statistics']['timings']:
          firstContentfulPaintMean   = 0
          firstContentfulPaintStddev = 0
          firstContentfulPaintMedian = 0
        else:
          firstContentfulPaintMean   = load['statistics']['timings']['timeToContentfulPaint']['mean']
          firstContentfulPaintStddev = load['statistics']['timings']['timeToContentfulPaint']['stddev']
          firstContentfulPaintMedian = load['statistics']['timings']['timeToContentfulPaint']['median']

        instance = {}
        instance['responseStartMean']                  = responseStartMean
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
        instance['timestamp']                          = load['info']['timestamp']
        instance['url']                                = url
        instance['loadNum']                            = loadNum
        report.append(instance)
        if (loadNum ) >= len(urlData['loads']):
          urlData['loads'].append([])

        urlData['loads'][loadNum].append(instance)
        loadNum = loadNum + 1


  # After each url
  results.append(urlData)
  sortedResults.append( sorted(report, key=itemgetter('timestamp')) )
  os.chdir("..")

numRows = 111

# print the results
print("\n")
for metric in metrics:
  print(metric + ":")
  print("-"*numRows)

  #for each url
  for j,l in enumerate(results):
    meanIndex = metric + "Mean"
    medianIndex = metric + "Median"
    stddevIndex = metric + "Stddev"
    baseValueMean = 0
    baseValueMedian = 0

    # for each load
    for loadNum,loadData in enumerate(results[j]['loads']):
      print("%-20.20s (load %2d)"% (results[j]['url'], loadNum), end="")
      print("| ", end="")
      # print out the metric for each variant
      for i,instance in enumerate(loadData):
        print("%11.2f"%  instance[meanIndex]   + "       | ", end="")
      print("")

    # and print the reload mean, std dev for each variant
    print("%-29.29s "% "reload mean" +"|", end="")
    for i,instance in enumerate(results[j]['loads'][0]):
      print("%12.2f"%  get_reload_mean(results, results[j]['url'], meanIndex, i), end="")
      print(" +-%4.0f"% get_reload_stddev(results, results[j]['url'], meanIndex, i) + "|", end="")

    print("")
    print("%-29.29s "% "reload median" +"|", end="")
    for i,instance in enumerate(results[j]['loads'][0]):
      print("%12.2f"%  get_reload_median(results, results[j]['url'], meanIndex, i) + "       |", end="")

    print("")
    print("-"*numRows)
  print("-"*numRows)
