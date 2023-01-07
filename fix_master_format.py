#!/usr/bin/env python

'''
This was just supposed to put the date field in every vehicle object
'''
import json

with open('master.json', 'r') as file:
  data = json.load(file)

date = data['date']
new_json = {}
for vehicle in data['cars']:
  entry = data['cars'][vehicle]
  entry['date'] = date
  new_json[vehicle] = entry

with open('master2.json', 'w+') as file:
  new_data = json.dumps(new_json, indent = 2)
  file.write(new_data)