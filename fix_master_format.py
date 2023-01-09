#!/usr/bin/env python

'''
This was just supposed to put the date field in every vehicle object
'''
import json
import time

with open('master.json', 'r') as file:
  data = json.load(file)

date = int(time.time())
new_json = {}
for vehicle in data:
  entry = data[vehicle]
  entry['date'] = int(str(date))
  new_json[vehicle] = entry

with open('master2.json', 'w+') as file:
  new_data = json.dumps(new_json, indent = 2)
  file.write(new_data)