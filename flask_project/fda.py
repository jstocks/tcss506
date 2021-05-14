import requests

def fda_api():
    api_key = 'b4ZyZnkYazIUGg0vHDTYTZBKV6QjlJoRxM1sGVp4'

    url = 'https://api.fda.gov/device/recall.json?search=event_date_created:[20150101+TO+20211231]&limit=100'

    data = requests.get(url).json()

    result = data.get('results', [])
    
    return result
