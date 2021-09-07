import requests
from bs4 import BeautifulSoup

res = requests.get('https://www.mlb.com/player/shohei-ohtani-660271?stats=career-r-hitting-mlb&year=2021')

soup = BeautifulSoup(res.text, 'html.parser')

scrollable = soup.find_all('div', {'class': 'responsive-datatable__scrollable'})

# scrollable = soup.find('div', class_='responsive-datatable__scrollable')
# a = scrollable.find_all('th', class_='no-sort col-3')

print (scrollable)