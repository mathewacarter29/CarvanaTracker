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
      limit = max_pages[type] + 1 if max_pages[type] <= 500 else 500
      for page in range(1, 5):
        curr_url = f'{url}/{type}'
        if page > 1:
          curr_url += '?page=' + str(page)       
        
        executor.submit(get_cars_on_page, curr_url, cars, lock)

  json_data = json.dumps(dict, indent = 2)

  # if the car_data folder does not exist, create it
  folder_name = 'car_data/'
  if not os.path.exists(folder_name):
    os.mkdir(folder_name)

  now = str(datetime.now())
  filename = now.replace(' ', '_') + '_carvana.json'
  filename = 'car_data/' + filename.replace(':', '-')
  with open(filename, 'w') as output_file:
    output_file.write(json_data)

  print(f'Data on {len(cars)} cars written to:', filename)

  # Now we want to compare the data we just pulled with the master file
  with open('master.json', 'r') as master_file:
    # This pulls the date too - we just want the cars
    master_data = json.load(master_file)
    master_cars = master_data['cars']
    car_added = False
    for vehicle in cars:
      # If the car is not in the master data, we want to add it
      if vehicle not in master_cars:
        car_added = True
        master_cars[vehicle] = cars[vehicle]
        print('Vehicle', vehicle, 'added to master list')
      else:
        # If it is in the master data, we want to compare the prices
        curr_price = cars[vehicle]['price']
        master_price = master_cars[vehicle]['price']
        if curr_price != master_price:
          print('current price:', curr_price, '--- old price:', master_price)

  if car_added:
    with open('master.json', 'w') as master_file:
      master_json_data = json.dumps(master_data, indent = 2)
      master_file.write(master_json_data)


if __name__ == '__main__':
  main()