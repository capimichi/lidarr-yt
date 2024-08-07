import json
from bs4 import BeautifulSoup
import requests


class OdesliClient:

    base_url = "https://song.link"

    def get_track_youtube_id(self, id):
        str_id = str(id)
        url = f"{self.base_url}/i/{str_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')

        youtube_id = None
        for link in links:
            if 'www.youtube.com' in link['href']:
                youtube_id = link['href'].split('=')[-1]
                break

        return youtube_id
