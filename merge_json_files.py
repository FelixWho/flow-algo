#! /usr/bin/env python3

import json
import glob

path = "data_flow2"
all_files = glob.glob(path + "/*.json")

raw_data = []

year, month = "2020", "01"

for fname in all_files:
	if "%s-%s" % (year, month) in fname:
		print(fname)
		f = open(fname, "r")
		raw_data += json.loads(f.read())

with open("merged_%s_%s.json" % (year, month), "w") as outfile:
	json.dump(raw_data, outfile)