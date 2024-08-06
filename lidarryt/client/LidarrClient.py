import requests


class LidarrClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_missing_tracks(self, page=1, page_size=10, sort_direction="descending", include_artist=False, monitored=True):
        url = f"{self.base_url}/api/v1/wanted/missing"
        params = {
            "page": page,
            "pageSize": page_size,
            "sortDirection": sort_direction,
            "includeArtist": include_artist,
            "monitored": monitored
        }
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        response = requests.get(url, headers={"X-Api-Key": self.api_key})
        data = response.json()
        return data

    def get_artist(self, artist_id):
        url = f"{self.base_url}/api/v1/artist/{artist_id}"
        response = requests.get(url, headers={"X-Api-Key": self.api_key})
        data = response.json()
        return data

    def get_album(self, album_id):
        url = f"{self.base_url}/api/v1/album/{album_id}"
        response = requests.get(url, headers={"X-Api-Key": self.api_key})
        data = response.json()
        return data

    def get_tracks(self, artist_id = None, album_id = None):
        if not artist_id and not album_id:
            raise ValueError("Either artist_id or album_id must be provided.")

        url = f"{self.base_url}/api/v1/track"
        params = {}
        if artist_id:
            params["artistId"] = artist_id
        if album_id:
            params["albumId"] = album_id
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        response = requests.get(url, headers={"X-Api-Key": self.api_key})
        data = response.json()
        return data

