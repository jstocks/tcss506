from datetime import date, timedelta
import requests
import csv


def generate_last_week_update():
    end_date = date.today().strftime("%Y%m%d")
    start_date = (date.today() - timedelta(days=15)).strftime("%Y%m%d")
    api_key = 'lKIZT2mPzq9RE0VqsDPyJpB5IbxbDzch8ne71Kbb'
    headers = {'Authorization': 'Bearer {}'.format(api_key)}
    search_api_url = f'https://api.fda.gov/device/recall.json?search=event_date_created:[{start_date}+TO+{end_date}]'
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


if __name__ == "__main__":
    print(generate_last_week_update())
