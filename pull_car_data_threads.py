import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import lxml
import cchardet

'''
Goes through a carvana URL and pulls all the cars on the page, adding them to dict
Needs to use lock param or else theres race condition
'''
def get_cars_on_page(url, dict, lock):
  page = requests.get(url)

  while page.status_code != 200:
    print('Error with status code', page.status_code, 'when accessing:', url)
    
    # We made too many requests too quickly, sleep for a bit then try again
    if page.status_code == 429:
      sleep_time = page.headers['Retry-After']
      print('Sleeping for', sleep_time, 'seconds')
      time.sleep(int(sleep_time))
    else:
      print('Status code', page.status_code, 'when trying:', url)
      return
    
    page = requests.get(url)

  soup = BeautifulSoup(page.content, 'lxml')

  results = soup.find_all(attrs={'class': 'result-tile'})

  # printing the raw html results of the get request
  # for div in results:
  #   print(div.prettify())

  # going by the data-qa attribute every field element has
  # mileage has other crap in it - split after weird character
  fields = ['make-model', 'trim-mileage', 'price', 'monthly-payment', 'get-it-by']
  data = {}
  for result in results:
    car_id = result.find('a').get('href')

    car_data = {'make-model': '', 'mileage': '', 'price': '', 'monthly-payment': '', 'get-it-by': ''}
    
    for field in fields:
      curr_field_value = result.find(attrs={'data-qa': field})
      field_text = curr_field_value.get_text()
      if field == 'trim-mileage':

        # the mileage part of a result tile also has info on the type of car,
        # so we have to split the string by the middle dot character and append
        # the car data to the make-model
        arr = field_text.split(' • ')
        car_data['make-model'] += ' - ' + arr[0]
        car_data['mileage'] = arr[1]

      elif field == 'get-it-by':
        car_data[field] = field_text.replace('Get it by ', '')

      elif field == 'price':
        # Take the $ and , out of the price so the JSON just has the price as a number
        price = field_text.replace('$', '')
        price = int(price.replace(',', ''))
        car_data[field] = price

      else:
        car_data[field] = field_text

    data[car_id] = car_data

  lock.acquire()
  prev = len(dict)
  dict.update(data)
  print(f'Got {len(dict) - prev} cars on page {url}')
  lock.release()

  # time.sleep(1)
  
'''
This just gets the maximum number of pages for each type of car
'''
def get_max_pages(url, page, max_pages_dict):
  try:
    req = requests.get(url)
  except:
    print('Error getting page:', url)
    return
  
  soup = BeautifulSoup(req.content, 'lxml')
  page_text = soup.find(attrs={'data-qa': 'pagination-text'}).get_text()
  max_page = page_text.split()[-1]
  max_pages_dict[page] = int(max_page)
