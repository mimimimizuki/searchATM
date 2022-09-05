import requests
import pandas as pd

url = "http://127.0.0.1:5000/getATMs"
payload = {
    "longitude":135.773228,
    "latitude":35.0305,
    "minute":10
}

r = requests.post(url, json=payload)

print(r.text)
print('-----------------------------')
payload = {
    "longitude":135.773228,
    "latitude":35.0305,
    "minute":10,
    'code':'9900',
    'weekday':6,
    'ATM_type':0,
    'time':'15:00'
}

r = requests.post('http://127.0.0.1:5000/filterATMs', json=payload)

print(r.text)
