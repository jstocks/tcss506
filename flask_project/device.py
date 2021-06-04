import requests
import datetime
import copy

def convert(html_date_format):
    dtobj = datetime.datetime.strptime(html_date_format, '%m/%d/%Y')
    return dtobj.date().strftime('%Y%m%d')

def device_api(limit=None, company=None, from_date=None, to_date=None):
    api_key = 'b4ZyZnkYazIUGg0vHDTYTZBKV6QjlJoRxM1sGVp4'
    base_url = 'https://api.fda.gov/device/event.json?'

    if limit is None:
        limit = 100
    base_url += "limit={}&".format(limit)

    # filter fields https://open.fda.gov/apis/query-syntax/
    # field:term+AND+field:term
    fields = dict()
    if company is not None and len(company) > 0:
        fields['manufacturer_d_name'] = company
    if from_date is not None and to_date is not None and len(from_date) > 0 and len(to_date) > 0:
        from_date = convert(from_date)
        to_date = convert(to_date)
        fields['date_of_event'] = "[{}+TO+{}]".format(from_date, to_date)
    if len(fields) > 0:
        base_url += "search="
        for key in fields.keys():
            if key == 'date_of_event':
                base_url += "{}:{}+AND+".format(key, fields[key])
            else:
                base_url += "{}={}+AND+".format(key, fields[key])
        base_url += "1"  # API won't accept AND operation without 2nd element

    # sort in descending
    base_url += "&sort=date_of_event:desc"

    # for debugging purpose
    # f = open("base_url.txt", "w")
    # f.write(base_url)
    # f.close()

    #url = 'https://api.fda.gov/device/event.json?search=date_of_event:[20150101+TO+20211231]&sort=date_of_event:desc&limit=100'

    data = requests.get(base_url).json()

    results = data.get('results', [])

    devices = []
    for result in results:
        for device in result['device']:

            # assume event_type always in the result tag
            device['event_type'] = result['event_type']

            # date_of_event sometimes not in the result tag
            if 'date_of_event' not in result.keys():
                device['date_of_event'] = ''
            else:
                device['date_of_event'] = result['date_of_event']

            if 'product_problems' not in result.keys():
                device['product_problems'] = ''
            else:
                device['product_problems'] = ','.join(result['product_problems'])

            # add new modified JSON element into the list
            devices.append(copy.deepcopy(device))
    
    return devices