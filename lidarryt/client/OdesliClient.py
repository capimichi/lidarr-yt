import json
from bs4 import BeautifulSoup
import requests


class OdesliClient:

    track_base_url = "https://song.link"
    album_base_url = "https://album.link"

    def get_track_youtube_id(self, id):
        str_id = str(id)
        url = f"{self.track_base_url}/i/{str_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')

        youtube_id = None
        for link in links:
            if 'www.youtube.com' in link['href']:
                youtube_id = link['href'].split('=')[-1]
                break

        return youtube_id

    def get_apple_music_id(self, id):
        url = self.get_track_apple_music_url(id, type="album")
        # remove after the question mark
        apple_music_id = url.split("?")[0]
        apple_music_id = apple_music_id.split("/")[-1]

        return apple_music_id

    def get_track_apple_music_url(self, id, type="track"):
        str_id = str(id)
        if(type == 'track'):
            url = f"{self.track_base_url}/i/{str_id}"
        else:
            url = f"{self.album_base_url}/i/{str_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')

        apple_music_url = None
        for link in links:
            if 'geo.music.apple.com' in link['href']:
                apple_music_url = link['href']
                break

        return apple_music_url
