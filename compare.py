#!/usr/bin/env python

from pull_car_data_threads import get_cars_on_page, get_max_pages

from datetime import datetime
import json
import os
import time
import concurrent.futures
import threading 
import sys

def main():
  now = str(datetime.now())
  if len(sys.argv) > 1:
    if '-l' in sys.argv:
      log = now.replace(' ', '_') + '_carvana.log'
      log = 'log/' + log.replace(':', '-')
      sys.stdout = open(log, 'w')

  url = "https://www.carvana.com/cars"
  car_types = ['trucks', 'hatchback', 'sedan', 'coupe', 'electric', 'suv']
  
  dict = {'date': int(time.time()), 'cars': {}}
  cars = dict['cars']

  # To get number of pages, search HTML for data-qa=pagination-text
  max_pages = {'trucks': 0, 'hatchback': 0, 'sedan': 0, 'coupe': 0, 'electric': 0, 'suv': 0}
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    for type in car_types:
      curr_url = f'{url}/{type}'
      executor.submit(get_max_pages, curr_url, type, max_pages)

  print(max_pages)
  
  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    lock = threading.Lock()
    for type in car_types:
      # Only go to page 500 because after that basically all cars are repeats
      limit = max_pages[type] + 1 if max_pages[type] <= 500 else 501
      for page in range(1, limit):
        curr_url = f'{url}/{type}'
        if page > 1:
          curr_url += '?page=' + str(page)       
        
        executor.submit(get_cars_on_page, curr_url, cars, lock)

  json_data = json.dumps(dict, indent = 2)

  # if the car_data folder does not exist, create it
  folder_name = 'car_data/'
  if not os.path.exists(folder_name):
    os.mkdir(folder_name)

  filename = now.replace(' ', '_') + '_carvana.json'
  filename = 'car_data/' + filename.replace(':', '-')
  with open(filename, 'w') as output_file:
    output_file.write(json_data)

  print(f'Data on {len(cars)} cars written to:', filename)

  # Now we want to compare the data we just pulled with the master file
  with open('master.json', 'r') as master_file:
    # This pulls the date too - we just want the cars
    master_data = json.load(master_file)
    cars_added = 0
    changed = []
    for vehicle in cars:
      # If the car is not in the master data, we want to add it
      if vehicle not in master_data:
        cars_added += 1
        cars[vehicle]['date'] = dict['date']
        master_data[vehicle] = cars[vehicle]
      elif cars[vehicle]['price'] != master_data[vehicle]['price']:
        # If it is in the master data, we want to compare the prices
        print(vehicle, '$' + str(master_data[vehicle]['price']), '--->', '$' + str(cars[vehicle]['price']))
        updated_car = {'vehicle_id': vehicle, 'curr_price': cars[vehicle]['price'], 'curr_date': dict['date'], 
          'master_price': master_data[vehicle]['price'], 'master_date': master_data[vehicle]['date']}
        changed.append(updated_car)
        master_data[vehicle]['price'] = cars[vehicle]['price']
        master_data[vehicle]['date'] = dict['date']

  if cars_added != 0 or len(changed) != 0:
    with open('master.json', 'w') as master_file:
      master_json_data = json.dumps(master_data, indent = 2)
      master_file.write(master_json_data)
    print('Cars added to master.json:', cars_added)

  if len(changed) != 0:
    # we want to check to see if this vehicle's price has already been changed (exists in file)
    with open('changed.json', 'r') as file:
      # if not, create a new entry with the start being master's date and price
      changed_json = json.load(file)
      for vehicle in changed:
        if vehicle['vehicle_id'] not in changed_json:
          changed_json[vehicle['vehicle_id']] = [{vehicle['master_date']: vehicle['master_price']}]

        change_entry = {vehicle['curr_date']: vehicle['curr_price']}
        changed_json[vehicle['vehicle_id']].append(change_entry)
    
    with open('changed.json', 'w') as file:
      file.write(json.dumps(changed_json, indent = 2))

      # if it does, we want to add the current date (dict['date']) and price to that objects list
    print('Number of updated prices:', len(changed))


if __name__ == '__main__':
  main()