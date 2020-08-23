#!/bin/python3

import sys
import re
import requests

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

def makeRequest(query):
    # The Search url is constant for amazon's results page
    # Simply appeneding the queury from earlier works

    search_url = "https://www.amazon.com/s?k="
    url = search_url + query
    
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

    r = requests.get(url, headers)

    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
            return None



def main():
    q = validateQueury()
    makeRequest(q)


main()
