#!/usr/bin/env python
import json
from datetime import date
import sys
import argparse
import time

'''
This program scans changed.json and gets the cars that have changed in price, sorted by
% price decrease (can be easily edited to be by price decrease in dollars)
'''
def main():

  parser = argparse.ArgumentParser(description='Get price decreases from Carvana')
  parser.add_argument('-m', '--month', action='store_true')
  parser.add_argument('-d', '--day', action='store_true')
  parser.add_argument('-r', '--results')
  args = parser.parse_args()
  
  if args.month and args.day:
    print("Only specify one time period - month or day")
    return
  
  dur = int(time.time())
  if args.month:
    # Number of seconds in 30 days
    dur -= 2_628_288
  elif args.day:
    # Number of seconds in a day
    dur -= 86400
  else:
    # If no time period is specified, then we will get discounts from all time
    dur = 0
  # We want to read the changed.json file and output the data in a friendly manner
  changed_file = open('changed.json', 'r')
  master_file = open('master.json', 'r')

  # We also want to get the type of car that is changed from master.json
  data = json.load(changed_file)
  master = json.load(master_file)
  results = []
  for car in data:
    prices = data[car]
    if int(list(prices[-1].keys())[-1]) >= dur:
      # any car in the changed.json file must also be in the master.json
      result = {'car': master[car], 'price_list': prices, 
      'price_change': list(prices[0].values())[0] - list(prices[-1].values())[-1],
      'percent_change': (list(prices[0].values())[0] - list(prices[-1].values())[-1]) / list(prices[0].values())[0],
      'url': f'https://www.carvana.com{car}'}
      results.append(result)

  results.sort(key=lambda x: x['percent_change'], reverse=True)
  limit = 10
  # Figure out how many results you want based on the cmd line args
  if args.results != None:
    if int(args.results) == -1:
      limit = len(results)
    else:
      limit = int(args.results) if int(args.results) <= len(results) else len(results)

  print('These are the biggest discounts on the cars Carvana has to offer:\n\n')
  for i in range(limit):
    print_car_data(results[i])
  changed_file.close()
  master_file.close()
  
'''
Prints the data for a single car object that contains the following fields:
car: master.json car object with all car data
price_list: list of prices along with the dates of those prices
price_change: the change in price from the earliest date to now
percent_change: the percent of the cars price it has changed by
url: the URL of the car on carvana's website
'''
def print_car_data(car_obj):
  car = car_obj['car']
  print(car_obj['url'])
  print('Name:', car['make-model'])
  print('Miles:', car['mileage'])
  print('Price: $' + str(car['price']))
  prices = car_obj['price_list']
  for index, kv in enumerate(prices):
    _date = list(kv.keys())[0]
    price = kv[_date]
    # The keys in JSON must always be strings, so we must cast _date to an int
    print(str(date.fromtimestamp(int(_date))) + ': $' + str(price), end='')
    if (index != len(prices) - 1):
      print(' ---> ', end='')
  print()
  ending = 'decrease' if car_obj['price_change'] > 0 else 'increase'
  print('$' + str(abs(car_obj['price_change'])), '(' + str(round(car_obj['percent_change'] * 100, 2)) + '%)', ending)
  # print(round(car_obj['percent_change'] * 100, 2), '% ', ending, sep='')
  print()
  

if __name__ == '__main__':
  main()