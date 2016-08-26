import requests
from jwp.jwjson import *

"Downloads each endpoint's raw json documentation"

# url to raw json of endpoints
RAW_URL = 'https://api.hypem.com/api-docs/{0}.json?key=swagger'
# a list of all available endpoints
ENDPOINTS = ['blogs', 'tracks', 'set', 'artists',
             'featured', 'tags', 'users', 'me', 'misc']


def download_docs():
    for endpoint in endpoints:
        r = requests.get(base_raw_doc.format(endpoint))
        write_json('raw_docs/{0}.json'.format(endpoint), r.json())

if __name__ == '__main___':
    download_docs()
