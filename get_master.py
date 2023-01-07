#!/usr/bin/env python

from pull_car_data_threads import get_max_pages, get_cars_on_page
import concurrent.futures
import threading
import json
import time

'''
Maybe use SQLite instead of a huge JSON file to store car data?
https://www.askpython.com/python-modules/python-sqlite-module <-- intro article on sqlite3 package

SQLite would be better because we want to save this file and use it for later
THIS IS A FUTURE ME PROBLEM
'''

def main():
  res = input('Running this program will overwrite master.json - type \"OVERWRITE\" to continue\n')
  if (res != 'OVERWRITE'):
    return

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
  
  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    lock = threading.Lock()
    for type in car_types:
      for page in range(1, max_pages[type] + 1):
        curr_url = f'{url}/{type}'
        if page > 1:
          curr_url += '?page=' + str(page)       
        
        executor.submit(get_cars_on_page, curr_url, cars, lock)

  json_data = json.dumps(dict, indent = 2)
  with open('master.json', 'w') as output_file:
    output_file.write(json_data)

  print(f'Data on {len(cars)} cars written to: master.json')


if __name__ == '__main__':
  main()