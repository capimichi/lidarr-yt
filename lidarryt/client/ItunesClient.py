import json

import requests


class ItunesClient:

    base_url = "https://itunes.apple.com"


    def search(self, search_term, entity="song, album, podcast"):

        # if search_term contains spaces, replace them with %20
        search_term = search_term.replace(" ", "%20")

        query_params = {
            "term": search_term,
            "country": "US",
            "entity": entity,
            "callback": "__jp61",
        }

        url = f"{self.base_url}/search?" + "&".join([f"{key}={value}" for key, value in query_params.items()])
        response = requests.get(url)

        # remove the callback function from the response
        response_text = response.text
        response_text = response_text.strip()
        response_text = response_text.replace("__jp61(", "")
        response_text = response_text[:-1]
        response_text = response_text[:-1]

        data = json.loads(response_text)

        return data
