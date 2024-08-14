import json
import urllib.parse

import requests
from injector import inject

from lidarryt.helper.ProxyHelper import ProxyHelper


class ItunesClient:

    base_url = "https://itunes.apple.com"

    proxy_helper: ProxyHelper

    @inject
    def __init__(self, proxy_helper: ProxyHelper):
        self.proxy_helper = proxy_helper


    def search(self, search_term, entity="song, album, podcast"):

        # if search_term contains spaces, replace them with %20
        # url encode the search term
        search_term = urllib.parse.quote(search_term)

        query_params = {
            "term": search_term,
            "country": "US",
            "entity": entity,
            "callback": "__jp61",
        }

        url = f"{self.base_url}/search?" + "&".join([f"{key}={value}" for key, value in query_params.items()])

        proxies = {}
        if(self.proxy_helper.is_proxy_enabled()):
            proxies = self.proxy_helper.get_requests_proxy()

        response = requests.get(url, proxies=proxies)

        # remove the callback function from the response
        response_text = response.text
        response_text = response_text.strip()
        response_text = response_text.replace("__jp61(", "")
        response_text = response_text[:-1]
        response_text = response_text[:-1]

        data = json.loads(response_text)

        return data
