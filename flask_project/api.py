import pandas as pd
import json
import plotly
import plotly.express as px
import requests
from flask_googlemaps import GoogleMaps, get_coordinates
from flask_googlemaps import Map
from datetime import date, timedelta
import csv


def device_api():
    api_key = 'b4ZyZnkYazIUGg0vHDTYTZBKV6QjlJoRxM1sGVp4'

    url = 'https://api.fda.gov/device/recall.json?search=event_date_created:[20150101+TO+20211231]&limit=100'

    data = requests.get(url).json()

    result = data.get('results', [])
    
    return result


def find_recall(start_date=20040101, end_date=20131231, limit1=10):
    api_key = 'lKIZT2mPzq9RE0VqsDPyJpB5IbxbDzch8ne71Kbb'
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    search_api_url = f'https://api.fda.gov/device/enforcement.json?search=report_date:[{start_date}+TO+{end_date}]&limit={limit1}'
    response = requests.get(search_api_url, headers=headers, timeout=5)
    data = response.json()
    return data["results"]


def graph_recall():
    recalls = find_recall()
    df = pd.DataFrame(
        {"Date": [recalls[i]['report_date'] for i in range(len(recalls))],
         "Recalling_firm": [recalls[i]['recalling_firm'] for i in range(len(recalls))]
         }
    )
    fig = px.line(df, x="Date", y="Recalling_firm")
    fig.update_yaxes(range=(0.0, 5), tick0=0.0, dtick=1)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def map_recall():
    apikey="AIzaSyBgvpdbo-uHRFsr3QPIqoq_P0jAnxIB9UQ"
    recalls=find_recall()
    markers=[];
    for recall in recalls[:10]:
        if "address_1" in recall:
            address="%20".join([recall["address_1"], recall["address_2"], recall["state"], recall["postal_code"]])
            try:
                location=get_coordinates(apikey,address)
                location['label']=recall['recalling_firm']
            except:
                continue
            markers.append(location)
    return Map(
        identifier="Tacoma",
        lat=47.2529,
        lng=-122.4443,
        markers=markers
        )


def generate_last_week_update():
    end_date = date.today().strftime("%Y%m%d")
    start_date = (date.today() - timedelta(days=60)).strftime("%Y%m%d")
    api_key = 'lKIZT2mPzq9RE0VqsDPyJpB5IbxbDzch8ne71Kbb'
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    search_api_url = f'https://api.fda.gov/device/event.json?search=date_of_event:[{start_date}+TO+{end_date}]'
    response = requests.get(search_api_url, headers=headers, timeout=5)
    data = response.json()
    if 'results' in data:
        result_data = data['results']
        # now we will open a file for writing
        data_file = open('data_file.csv', 'w')

        # create the csv writer object
        csv_writer = csv.writer(data_file)

        # Counter variable used for writing
        # headers to the CSV file
        count = 0
        for result in result_data:
            if count == 0:
                # Writing headers of CSV file
                header = result.keys()
                csv_writer.writerow(header)
                count += 1
            # Writing data of CSV file
            csv_writer.writerow(result.values())

        data_file.close()
        return True
    else:
        return False