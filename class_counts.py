#!/usr/bin/env python3
# This file is covered by the LICENSE file in the root of this project.

import csv
import argparse
import os
import yaml
import numpy as np
import collections
from auxiliary.laserscan import SemLaserScan


if __name__ == '__main__':
  parser = argparse.ArgumentParser("./content.py")
  parser.add_argument(
      '--dataset', '-d',
      type=str,
      required=True,
      help='Dataset to calculate content. No Default',
  )
  parser.add_argument(
      '--config', '-c',
      type=str,
      required=False,
      default="config/semantic-kitti.yaml",
      help='Dataset config file. Defaults to %(default)s',
  )
  FLAGS, unparsed = parser.parse_known_args()

  # open config file
  try:
    print("Opening config file %s" % FLAGS.config)
    CFG = yaml.safe_load(open(FLAGS.config, 'r'))
  except Exception as e:
    print(e)
    print("Error opening yaml file.")
    quit()

  # get training sequences to calculate statistics
  sequences = CFG["split"]["train"]
  print("Analyzing sequences", sequences)

  labels_arr = [" "]

  for key, _ in CFG["labels"].items():
    labels_arr.append(_)

  labels_arr.append("Total")

  # write labels of each available class
  with open("scenes_overview.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(labels_arr)

  # create content accumulator
  iternum = 0
  total = 0

  # iterate over sequences
  for seq in sequences:
    seq_array = ["seq " + str(seq)]
    seq_accum = {}
    seq_total = 0
    for key, _ in CFG["labels"].items():
      seq_accum[key] = 0

    # make seq string
    print("*" * 80)
    seqstr = '{0:02d}'.format(int(seq))
    print("parsing seq {}".format(seq))

    # does sequence folder exist?
    scan_paths = os.path.join(FLAGS.dataset, "sequences",
                              seqstr, "velodyne")
    if os.path.isdir(scan_paths):
      print("Sequence folder exists!")
    else:
      print("Sequence folder doesn't exist! Exiting...")
      quit()

    # populate the pointclouds
    scan_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(scan_paths)) for f in fn]
    scan_names.sort()

    # does sequence folder exist?
    label_paths = os.path.join(FLAGS.dataset, "sequences",
                               seqstr, "labels")
    if os.path.isdir(label_paths):
      print("Labels folder exists!")
    else:
      print("Labels folder doesn't exist! Exiting...")
      quit()

    # populate the pointclouds
    label_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(label_paths)) for f in fn]
    label_names.sort()

    # create a scan
    scan = SemLaserScan(CFG["color_map"], project=False)

    for idx in range(len(scan_names)):
      # open scan
      scan.open_scan(scan_names[idx])
      scan.open_label(label_names[idx])
      # make histogram and accumulate
      count = np.bincount(scan.sem_label)
      seq_total += count.sum()
      for key, data in seq_accum.items():
        if count.size > key:
          seq_accum[key] += count[key]
          # zero the count
          count[key] = 0
      for i, c in enumerate(count):
        if c > 0:
          print("wrong label ", i, ", nr: ", c)

    seq_accum = collections.OrderedDict(
        sorted(seq_accum.items(), key=lambda t: t[0]))

    # print and send to total
    total += seq_total
    print("seq ", seqstr, "total", seq_total)
    for key, data in seq_accum.items():
      seq_array.append(data)
    seq_array.append(total)

    # write number of pixels for each class in the seq
    with open("scenes_overview.csv", 'a', newline='') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(seq_array)
