import os
from datetime import datetime

from injector import inject


class LidarrFsHelper:

    root_folder : str = None
    preferred_codec : str = "mp3"

    @inject
    def __init__(self, root_folder):
        self.root_folder = root_folder.rstrip("/")

    def get_lidarr_album_dir(self, album):
        parsed_date = datetime.fromisoformat(album["releaseDate"].replace("Z", "+00:00"))
        album_year = parsed_date.year
        artist_name = album["artist"]['artistName']
        album_name = album["title"]
        album_str = album_name.replace("/", " ")
        album_folder = f"{album_str} ({album_year})"
        album_dir = os.path.join(self.root_folder, artist_name, album_folder)

        return album_dir


    def get_lidarr_track_file(self, album, track_title, track_number, disc_number):
        album_dir = self.get_lidarr_album_dir(album)
        artist_str = os.path.basename(album["artist"]['artistName'])
        album_name = album["title"]
        album_str = album_name.replace("/", " ")
        title_str = track_title.replace("/", " ")
        track_number = str(track_number).zfill(2)
        disc_number = str(disc_number).zfill(2)

        filename = f"{artist_str} - {album_str} - {disc_number}x{track_number} - {title_str}.{self.preferred_codec}"
        full_file_path = os.path.join(album_dir, filename)

        return full_file_path

