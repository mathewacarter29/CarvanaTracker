#!/usr/bin/env python
import json
from datetime import date

def main():
  # We want to read the changed.json file and output the data in a friendly manner
  changed_file = open('changed.json', 'r')
  master_file = open('master.json', 'r')

  # We also want to get the type of car that is changed from master.json
  data = json.load(changed_file)
  master = json.load(master_file)
  for car in data:
    prices = data[car]
    # any car in the changed.json file must also be in the master.json
    car_name = master[car]['make-model']
    print(car_name)
    for index, kv in enumerate(prices):
      _date = list(kv.keys())[0]
      price = kv[_date]
      print(str(date.fromtimestamp(int(_date))) + ': $' + str(price), end='')
      if (index != len(prices) - 1):
        print(' ---> ', end='')
    print('\nChange in price: $', list(prices[0].values())[0] - list(prices[-1].values())[-1], sep='')
    print('\n\n')

  changed_file.close()
  master_file.close()
  

if __name__ == '__main__':
  main()