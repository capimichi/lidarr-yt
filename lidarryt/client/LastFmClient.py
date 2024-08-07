import requests


class LastFmClient:

    base_url = "https://ws.audioscrobbler.com/2.0"


    def __init__(self, api_key):
        self.api_key = api_key


    def get_album_info(self, artist_name, album_title):
        query_params = {
            "method": "album.getinfo",
            "api_key": self.api_key,
            "artist": artist_name,
            "album": album_title,
            "format": "json"
        }

        url = f"{self.base_url}/?" + "&".join([f"{key}={value}" for key, value in query_params.items()])
        response = requests.get(url)
        return response.json()
