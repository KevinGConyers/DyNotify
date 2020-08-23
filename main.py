#!/bin/python3
import sys
import re
import requests
import traceback
import json
from lxml.html import fromstring
from itertools import cycle
from selectorlib import Extractor

# Init proxies requests some proxies from a free proxy list
# These are used to get around amazon blocking unkown bots
def initProxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)

    return proxies

def validateQueury():
    if len(sys.argv) < 2:
        print("Please provide a query")
        exit()


    check = ' '.join(sys.argv[1:])
    val_match = re.search("[^a-zA-Z0-9\s']", check)
    if val_match:
        print("Only letters, numbers spaces and \"\'\"are allowed in query")
        exit()

    query = "+".join(sys.argv[1:]) #return query with http request seperator
    return query

def makeAmazonRequest(query, proxy):
    # The Search url is constant for amazon's results page
    # Simply appeneding the query from earlier works

    search_url = "https://www.amazon.com/s?k=<q>&ref=nb_sb_noss_2"
    url = re.sub("\<q\>", query, search_url)
    print(url)

    #Found these header's via googling
    headers = { 
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    try:
        r = requests.get(url,proxies={"http": proxy, "https": proxy},headers=headers)
        if r.status_code > 500:
            print("Proxy %s failed"%proxy)
            if "To discuss automated access to Amazon data please contact" in r.text:
                print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
            else:
                print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
                return None
        elif r.status_code >= 200 and r.status_code <= 299:
            print(r.status_code)
            results_extractor = Extractor.from_yaml_file('./search_data.yml')
            data = results_extractor.extract(r.text)
            print(data)
            return data # Short circuit as soon as a good request is recieved
        else:
            print("Unhandled status code")
            return None
            
    except Exception as e:
        print(e)
        # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work. 
        # We will just skip retries as its beyond the scope of this demo and we are only downloading a single url 
        print("Skipping. Connnection error")

def requestsDriver(q, proxy_pool):
    data = None
    for i in range(1,11):
        #Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d"%i)
        data = makeAmazonRequest(q, proxy)
        if data:
            break
    if data != None:
        extractAndSaveData(data)
    else:
        print("unspecified error with request")


def extractAndSaveData(data):
    print("starting data extraction")
    with open('results.json', 'w') as result_file:
        for prod in data['product']:
            print(prod)
            try:
                json.dump(prod, result_file)
                result_file.write("\n")
            except Exception as e:
                if "TypeError" in e:
                    print("Network did something wierd, retrying")
                    main();
                else:
                    print("File issues")

def main():
    q = validateQueury()

    proxies = initProxies()
    proxy_pool = cycle(proxies)
    requestsDriver(q, proxy_pool)

    
main()
