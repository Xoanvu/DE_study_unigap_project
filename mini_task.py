import requests as rq

url = 'http://coderbyte.com/api/challenges/json/age-counting'
results = rq.get(url)
results.raise_for_status()
data = results.json()

print(data)