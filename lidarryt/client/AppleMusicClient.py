import json
from typing import Optional

from bs4 import BeautifulSoup
import requests

from lidarryt.model.AppleAlbumData import AppleAlbumData


class AppleMusicClient:

    base_url = "https://music.apple.com"

    def get_album_data(self, id) -> Optional[AppleAlbumData]:
        str_id = str(id)
        url = f"{self.base_url}/sm/album/_/" + str_id
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.text
            if 'AlbumDetailPageIntent' in script_text:
                data = json.loads(script_text)
                if(len(data) > 0 and "intent" in data[0]):
                    album_data = AppleAlbumData(data[0])
                    return album_data

        return None
