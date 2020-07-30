import os
from datetime import datetime
import json
import urllib.request
import urllib.parse
import re
import ssl


WITH_PROXY = False  # on/off proxy. Default is off
PROXY_ADDRESS = ''
PROXY_PORT = ''
PROXY_PROTOCOL = ''

API_URL = 'https://bt.group-ib.com/'
API_USER = ''  # your user
API_KEY = ''  # your API KEY

DATA_DIR = 'data/'  # directory for saving data

LIMIT = 1000  # limit for most data
BIG_DATA_LIMIT = 10  # limit for big data

LANG_DEF = 1
LANG_RUS = 2
LANG_ENG = 3


DEFAULT_DATES = {
    "accs": "2019-08-26",
    "cards":"2019-08-26",
    "imei": "2019-08-26",
    "mules": "2019-08-26",
    "phishing": "2019-08-26",
    "ddos": "2019-08-26",
    "hacktivism": "2019-08-26",
    "sample": "2019-08-26",
    "threats": "2019-08-26",
    "tornodes": "2019-08-26",
    "proxy": "2019-08-26",
    "socks": "2019-08-26",
    "domain": "2019-08-26",
    "ssl": "2019-08-26",
    "advert": "2019-08-26",
    "mobileapp": "2019-08-26",
    "phishingkit": "2019-08-26",
    "leaks": "2019-08-26"
}


# Send request to API
def send(action, last, lang):

    url = API_URL
    user = API_USER
    api_key = API_KEY

    if action == 'sample' or action == 'leaks':
        limit = BIG_DATA_LIMIT
    else :
        limit = LIMIT

    headers = {
        'Accept': 'application/json',
        'X-Auth-Login': user,
        'X-Auth-Key': api_key,
        'Connection': 'Keep-Alive',
        'Keep-Alive': 30
    }

    request_params = {
        "module": "get",
        "action": action,
        "limit": limit,
        "last": last
    }

    if lang is not None:
        request_params["lang"] = lang

    url = urllib.parse.urljoin(url, '?' + urllib.parse.urlencode(request_params))

    log('>>Request: ' + url)

    #if WITH_PROXY:
    #    proxy_handler = '{"https": "https://127.0.0.1:3005"}'
    #    proxy_handler = json.loads(proxy_handler)
    #    proxy = urllib.request.ProxyHandler(proxy_handler)
    #    opener = urllib.request.build_opener(proxy)
    #    urllib.request.install_opener(opener)

    request = urllib.request.Request(url)

    if WITH_PROXY:
        proxy_host = PROXY_ADDRESS + ':' + PROXY_PORT
        request.set_proxy(proxy_host, PROXY_PROTOCOL)

    for key, value in headers.items():
        request.add_header(key, value)

    gcontext = ssl._create_unverified_context()
    handle = urllib.request.urlopen(request, context=gcontext)
    response = handle.read().decode('utf-8')

    result = json.loads(response)

    for_change_array = { "date_begin": "1971-01-01 00:00:00", "date_end": "1971-01-01 00:00:00",
                         "date_detected": "1971-01-01 00:00:00", "advert_domain_registered": "1971-01-01 00:00:00",
                         "date_registered": "1971-01-01", "date_expired": "1971-01-01",
                         "date_published": "1971-01-01", "date_updated": "1971-01-01",
                         "date_blocked": "1971-01-01 00:00:00",
                         "date_not_before": "1971-01-01", "date_not_after": "1971-01-01",
                         "date_compromised": "1971-01-01 00:00:00",
                         "date_add": "1971-01-01 00:00:00", "date_incident": "1971-01-01 00:00:00",
                         "operation_date": "1971-01-01 00:00:00",
                         "date_publish": "1971-01-01 00:00:00",
                         "date": "1971-01-01 00:00:00",
                         "date_first_seen": "1971-01-01 00:00:00",
                         "target_port": "0", "size": "0", "vt_all": "-", "vt_detected": "-", "phishing_kit_file_size": "0",
                         "rows_count": "0" }

    for elem in result["data"]["new"]:
        for key, val in for_change_array.items():
            if key in elem["attrs"] and elem["attrs"][key] == None:
                elem["attrs"][key] = val

    try:
        error = result['error']
        raise Exception(error)
    except KeyError:
        pass

    try:
        count = result["data"]['count']
        last = result["data"]['last']
        limit = result["data"]['limit']
        count_new = len(result["data"]["new"])
        count_del = len(result["data"]["del"])
        log('<<Response param: count = {0}, last = {1}, limit = {2}, count new = {3}, count del = {4}'.format(count, last, limit, count_new, count_del))
    except KeyError:
        print('Bad response:' + response)

    return result


# Console loging
def log(str):
    now = datetime.now()
    str = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}\t".format(now) + str
    print(str)


# Saving last value "last"
def set_last(action, last):
    hd = open(DATA_DIR + action + '.last', 'w')
    hd.write(str(last))


def get_last_by_date(action, date):
    url = "https://bt.group-ib.com/?module=get&action=get_last&date={0}&type={1}".format(date, action)

    log("Taking 'last' value from server by date {0}".format(date))

    headers = {
        "Accept": "application/json",
        "X-Auth-Login": API_USER,
        "X-Auth-Key": API_KEY
    }

    request = urllib.request.Request(url)

    if WITH_PROXY:
        proxy_host = PROXY_ADDRESS + ':' + PROXY_PORT
        request.set_proxy(proxy_host, PROXY_PROTOCOL)

    for key, value in headers.items():
        request.add_header(key, value)

    gcontext = ssl._create_unverified_context()
    handle = urllib.request.urlopen(request, context=gcontext)
    response = handle.read().decode('utf-8')

    result = json.loads(response)

    return result["data"]


# Getting last value "last"
def get_last(action):
    try:
        hd = open(DATA_DIR + action + '.last', 'r')
    except OSError:
        #return 0
        return get_last_by_date(action, DEFAULT_DATES[action])

    try:
        result = int(hd.read())
    except ValueError:
        #result = 0
        result = get_last_by_date(action, DEFAULT_DATES[action])

    return result


def validIP(address):
    parts = str(address).split(".")
    if len(parts) != 4:
        return False
    for item in parts:
        if not 0 <= int(item) <= 255:
            return False
    return True


def SeizeThreats(oldResult):
    newResult = {}
    try:
        newResult["status"] = oldResult["status"]
        newResult["data"] = {}
        newResult["data"]["last"] = oldResult["data"]["last"]
        newResult["data"]["limit"] = oldResult["data"]["limit"]
        newResult["data"]["count"] = oldResult["data"]["count"]
        newResult["data"]["new"] = []
        for old in oldResult["data"]["new"]:
            for ind in old["attrs"]["indicators"]:
                try:
                    for val in ind["value"]:
                        new = {}
                        new["id"] = old["id"]
                        new["attrs"] = {}
                        if ind["type"] in ["cnc", "ip", "anonymization"]:
                            if validIP(val):
                                new["attrs"]["ip"] = val
                                new["attrs"]["url"] = ""
                                new["attrs"]["domain"] = ""
                            elif "/" in val:
                                new["attrs"]["ip"] = ""
                                new["attrs"]["url"] = val
                                new["attrs"]["domain"]= ""
                            else:
                                new["attrs"]["ip"] = ""
                                new["attrs"]["url"] = ""
                                new["attrs"]["domain"] = val
                        elif ind["type"] == "domain":
                            new["attrs"]["ip"] = ""
                            new["attrs"]["url"] = ""
                            new["attrs"]["domain"] = val
                        elif ind["type"] == "url":
                            new["attrs"]["ip"] = ""
                            new["attrs"]["url"] = val
                            new["attrs"]["domain"] = ""
                        if len(new["attrs"]) != 0:
                            newResult["data"]["new"].append(new)
                except:
                	pass
    except:
    	pass
    return newResult


# Getting new data for section
def get_data(action, lang=None):
    log('Start load ' + action)

    dir = DATA_DIR + action

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    last = get_last(action)
    total_new = 0

    while True:
        result = send(action, last, lang)

        if last == result["data"]["last"]:
            break

        last = result["data"]["last"]
        set_last(action, last)

        total_new += len(result["data"]["new"])

        if len(result["data"]["new"]) or len(result["data"]["del"]):
            hd = open(DATA_DIR + 'data_{0}.json'.format(last), "w")
            if action == "threats":
                result = SeizeThreats(result)
            json_data = re.sub('\{"id"','{"type": "'+action+'", "id"',json.dumps(result["data"]))
            json_data = re.sub(':\snull,',': "",',json_data)
            hd.write(json_data)
            hd.close()

    log('Total new: {0}'.format(total_new))
    log('=====================================================================')

if __name__ == "__main__":
    # compromised data
    #get_data('accs')
    #get_data('cards')
    #get_data('imei')
    #get_data('mules')

    # attacks
    #get_data('ddos')

    # brand abuse
    #get_data('domain')
    #get_data('ssl')
    #get_data('phishing')
    #get_data('advert')
    #get_data('mobileapp')
    #get_data('phishingkit')

    # suspicious ip
    #get_data('tornodes')
    #get_data('proxy')
    #get_data('socks')

    # leaks
    #get_data('leaks')

    # hacktivism
    #get_data('hacktivism', LANG_ENG)

    # targeted malware
    #get_data('sample')

    # threats
    get_data('threats', LANG_ENG)
