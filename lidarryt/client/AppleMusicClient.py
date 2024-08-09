import json
from bs4 import BeautifulSoup
import requests


class AppleMusicClient:

    base_url = "https://music.apple.com"

    def get_album_data(self, id):
        str_id = str(id)
        url = f"{self.base_url}/sm/album/_/" + str_id
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.text
            if 'MusicAlbum' in script_text:
                data = json.loads(script_text)
                if("tracks" in data):
                    return data

        return None
