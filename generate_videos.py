#!/usr/bin/env python
from __future__ import print_function
import argparse
import json
import os.path
import glob
import sys
import math
import statistics
import subprocess
from shutil import copyfile
from operator import itemgetter

global options

parser = argparse.ArgumentParser(
    description="",
    prog="generate_videos",
)

parser.add_argument(
    "directory",
    default="browsertime",
    help="Directory to process",
)


parser.add_argument(
    "-s", "--speedindex",
    action="store_true",
    default=False,
    help="Use Median SpeedIndex",
)

parser.add_argument(
    "-c", "--contentfulspeedindex",
    action="store_true",
    default=False,
    help="Use Median ContentfulSpeedIndex",
)

parser.add_argument(
    "-p", "--perceptualspeedindex",
    action="store_true",
    default=False,
    help="Use Median PerceptualSpeedIndex",
)

parser.add_argument(
    "-l", "--pageload",
    action="store_true",
    default=False,
    help="Use Median pageload",
)

parser.add_argument(
    "--videos",
    action="store_true",
    default=False,
    help="Generate side-by-side videos",
)

parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    default=False,
    help="Verbose output",
)

options = parser.parse_args()

os.chdir(options.directory);
files = glob.glob("*")

files_with_url = []
for url in files:
  os.chdir(url)
  sessions = glob.glob("*")
  entry = {}
  if options.verbose:
    print(url)
    print(sessions[0])
  with open(sessions[0] + "/browsertime.json") as f:
    data = json.load(f)
    entry['url'] = data[0]['info']['url'].encode("utf8","ignore")
    entry['dir'] = url
    files_with_url.append(entry)
  os.chdir('..')

if options.verbose:
  print(files_with_url)

sortedFiles = sorted(files_with_url, key=itemgetter('url'))

sortedResults = []
for j,entry in enumerate(sortedFiles):
  if options.verbose:
    print(entry)
  url=entry['dir']
  os.chdir(url)

  report = []
  sessions = glob.glob("*")
  skipURL=0
  for k,session in enumerate(sessions):
    with open(session + "/browsertime.json") as f:
      data = json.load(f)

      pageLoadTime = []
      SpeedIndex = []
      PerceptualSpeedIndex = []
      ContentfulSpeedIndex = []
      FirstVisualChange = []
      VisualComplete85 = []

      iterations=len(data[0]['browserScripts'])
      for i in range(0,iterations):
        pageLoadTime.append( data[0]['browserScripts'][i]['timings']['pageTimings']['pageLoadTime'] )

      iterations=len(data[0]['visualMetrics'])
      for i in range(0,iterations):
        SpeedIndex.append( data[0]['visualMetrics'][i]['SpeedIndex'] )
        PerceptualSpeedIndex.append( data[0]['visualMetrics'][i]['PerceptualSpeedIndex'] )
        ContentfulSpeedIndex.append( data[0]['visualMetrics'][i]['ContentfulSpeedIndex'] )
        FirstVisualChange.append( data[0]['visualMetrics'][i]['FirstVisualChange'] )
        VisualComplete85.append( data[0]['visualMetrics'][i]['VisualComplete85'] )

      # no switch in python
      if options.speedindex:
        metric = SpeedIndex
      elif options.contentfulspeedindex:
        metric = ContentfulSpeedIndex
      elif options.perceptualspeedindex:
        metric = PerceptualSpeedIndex
      elif options.pageload:
        metric = pageLoadTime
      else:
        metric = SpeedIndex
      # TODO FVC/VC85
        
      median=statistics.median(metric)
      bestVideo = url + '/' + session + '/' + data[0]['files']['video'][0]
      lowestDiff=abs(metric[0]-median)
      lowestIndex = 0
      for i in range(1,iterations):
        diff=abs(metric[i]-median)
        if options.verbose:
          print ('Value: ' + str(metric[i]) + ' diff: ' + str(diff) + ' median: ' + str(median) )
        if diff < lowestDiff:
          if options.videos:
            bestVideo = url + '/' + session + '/' + data[0]['files']['video'][i]
          if options.verbose:
            print('found new best video: ' + bestVideo)
          lowestDiff = diff
          lowestIndex = i;

      # if not os.path.exists(bestVideo):
      #   print( '** best not found **')
      #   for i in range(1,iterations):
      #     bestVideo = url + '/' + session + '/' + data[0]['files']['video'][i]
      #     if os.path.exists(bestVideo):
      #       break

      print("-------------------------------------------------------")
      print(url + " -- " + session)
      if options.videos:
        print(" bestVideo " + bestVideo)
      if options.verbose:
        print("lowestDiff = " + str(lowestDiff))
        print(SpeedIndex)
      print("Median = " + str(statistics.median(SpeedIndex)) + ", median index = " + str(lowestIndex))

      instance = {}
      instance['pageLoadTimeMedian']        = statistics.median(pageLoadTime);
      instance['pageLoadTimeStdev']       = statistics.stdev(pageLoadTime);
      instance['SpeedIndexMedian']          = statistics.median(SpeedIndex);
      instance['SpeedIndexStdev']         = statistics.stdev(SpeedIndex);
      instance['PerceptualSpeedIndexMedian']  = statistics.median(PerceptualSpeedIndex);
      instance['PerceptualSpeedIndexStdev'] = statistics.stdev(PerceptualSpeedIndex);
      instance['ContentfulSpeedIndexMedian']  = statistics.median(ContentfulSpeedIndex);
      instance['ContentfulSpeedIndexStdev'] = statistics.stdev(ContentfulSpeedIndex);
      instance['FirstVisualChangeMedian']   = statistics.median(FirstVisualChange);
      instance['FirstVisualChangeStdev']  = statistics.stdev(FirstVisualChange);
      instance['VisualComplete85Median']    = statistics.median(VisualComplete85);
      instance['VisualComplete85Stdev']   = statistics.stdev(VisualComplete85);
      instance['value']                   = session
      instance['timestamp']               = data[0]['info']['timestamp']
      instance['url']                     = url
      instance['video']                   = bestVideo
      instance['dir']                     = session.upper()
      report.append(instance)


  sortedResults.append( sorted(report, key=itemgetter('timestamp')) )
  os.chdir("..")


if options.videos:
  for j,l in enumerate(sortedResults):
    url=sortedResults[j][0]["url"]

    video1=sortedResults[j][0]['video']
    video2=sortedResults[j][1]['video']

    #print(R"ffmpeg -i " + video1 + R" -vf drawtext='text=" + sortedResults[j][0]['dir'] + R":fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10:scale=trunc(iw/2)*2:trunc(ih/2)*2' -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -codec:a copy input1.mp4")
    #exit()

    # command = R"ffmpeg -i " + video1 + R" -vf drawtext='text=" + sortedResults[j][0]['dir'] + R":fontfile=/users/acreskey/fonts/Raleway/Raleway-Bold.ttf:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10',scale='trunc(iw/2)*2:trunc(ih/2)*2' -codec:a copy input1.mp4"
    # print(command)
    # os.system(command)

    # command = R"ffmpeg -i " + video2 + R" -vf drawtext='text=" + sortedResults[j][1]['dir'] + R":fontfile=/users/acreskey/fonts/Raleway/Raleway-Bold.ttf:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10',scale='trunc(iw/2)*2:trunc(ih/2)*2' -codec:a copy input2.mp4"
    # print(command)
    # os.system(command)
    
    # command = R"ffmpeg -i input1.mp4" + R" -i input2.mp4" + R" -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast " + R"../videos/" + str(j).zfill(3) + "-" + url + ".mp4"
    # print(command)
    # os.system(command)
    
    # command = R"ffmpeg -i " + video1 + R" -vf drawtext='text=" + sortedResults[j][0]['dir'] + R":fontfile=/users/acreskey/fonts/Raleway/Raleway-Bold.ttf:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10',scale='trunc(iw/2)*2:trunc(ih/2)*2' -codec:a copy input1.mp4"
    # print(command)
    # os.system(command)
    
    # command = R"ffmpeg -i " + video2 + R" -vf drawtext='text=" + sortedResults[j][1]['dir'] + R":fontfile=/users/acreskey/fonts/Raleway/Raleway-Bold.ttf:fontcolor=white:fontsize=24:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10',scale='trunc(iw/2)*2:trunc(ih/2)*2' -codec:a copy input2.mp4"
    # print(command)
    # os.system(command)
    
    #command = R"ffmpeg -i " + video1 + R" -i " + video2 + R" -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast " + R"../videos/" + str(j).zfill(3) + "-" + url + ".mp4"
    
    command = R"ffmpeg -i " + video1 + R" -i " + video2 + R" -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast " + R"../videos/" + str(j).zfill(3) + "-" + url + ".mp4"

    print(command)
    os.system(command)

    # os.remove('input1.mp4')
    # os.remove('input2.mp4')
    exit

    print("")
