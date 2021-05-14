import requests

def fda_api():
    api_key = 'b4ZyZnkYazIUGg0vHDTYTZBKV6QjlJoRxM1sGVp4'

    url = 'https://api.fda.gov/device/enforcement.json?search=report_date:[20210101+TO+20211231]&limit=10'

    data = requests.get(url).json()

    result = data.get('results', [])
    
    return result
