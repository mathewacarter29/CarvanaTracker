import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys

now = str(datetime.now())
filename = now.replace(' ', '_') + '_carvana.txt'
filename = filename.replace(':', ';')
sys.stdout = open(filename, 'w')


url = "https://www.carvana.com/cars/suv"

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')


results = soup.find_all(attrs={'class': 'result-tile'})

# printing the raw html results of the get request
# for div in results:
#   print(div.prettify())

# going by the data-qa attribute every field element has
# fuck shipping cost?
# mileage has other crap in it - split after weird character
fields = ['make-model', 'trim-mileage', 'price', 'monthly-payment', 'shipping-cost', 'get-it-by']
fields_readable= ['Car Name', 'Mileage', 'Price', 'Monthly Payment', 'Shipping Cost', 'Delivery']

for result in results:
  for index, field in enumerate(fields):
    curr_field_value = result.find(attrs={'data-qa': field})

    print(fields_readable[index] + ':', curr_field_value.get_text())

  print()

# print(results[0].prettify())

