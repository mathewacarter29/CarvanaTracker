#!/usr/bin/env python

from pull_car_data_threads import get_cars_on_page, get_max_pages

from datetime import datetime
import json
import os
import time
import concurrent.futures
import threading 

def main():
  url = "https://www.carvana.com/cars"
  car_types = ['trucks', 'hatchback', 'sedan', 'coupe', 'electric', 'suv']
  dict = {}

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
      # for page in range(1, max_pages[type] + 1):
      for page in range(1, 6):
        curr_url = f'{url}/{type}'
        if page > 1:
          curr_url += '?page=' + str(page)       
        
        executor.submit(get_cars_on_page, curr_url, dict, lock)

  json_data = json.dumps(dict, indent = 4)

  # if the car_data folder does not exist, create it
  folder_name = 'car_data/'
  if not os.path.exists(folder_name):
    os.mkdir(folder_name)

  now = str(datetime.now())
  filename = now.replace(' ', '_') + '_carvana.json'
  filename = 'car_data/' + filename.replace(':', '-')
  with open(filename, 'w') as output_file:
    output_file.write(json_data)

  print(f'Data on {len(dict)} cars written to:', filename)

  # Now we want to compare the data we just pulled with the master file
  master_file = open('master.json')
  master_data = json.load(master_file)
  car_added = False
  for vehicle in dict:
    # If the car is not in the master data, we want to add it
    if vehicle not in master_data:
      car_added = True
      master_data[vehicle] = dict[vehicle]
      print('Vehicle', vehicle, 'added to master list')
    else:
      # If it is in the master data, we want to compare the prices
      curr_price = dict[vehicle]['price']
      master_price = master_data[vehicle]['price']
      print('current price:', curr_price)
      print('master price:', master_price)

if __name__ == '__main__':
  main()