import os
from datetime import datetime

from injector import inject


class LidarrFsHelper:

    root_folder : str = None
    preferred_codec : str = "mp3"

    @inject
    def __init__(self, root_folder):
        self.root_folder = root_folder

    def get_artist_dir(self, artist_name):
        parsed_artist_name = artist_name.replace("/", " ")
        return os.path.join(self.root_folder, parsed_artist_name)

    def get_album_dir(self, artist_name, album_title, album_release_year):
        parsed_album_title = album_title.replace("/", " ")
        return os.path.join(self.get_artist_dir(artist_name), f"{parsed_album_title} ({album_release_year})")

    def get_track_file(self, artist_name, album_title, album_release_year, track_title, disc_number, track_number):
        parsed_track_number = str(track_number).zfill(2)
        parsed_disc_number = str(disc_number).zfill(2)
        parsed_artist_name = artist_name.replace("/", " ")
        parsed_album_title = album_title.replace("/", " ")
        parsed_track_title = track_title.replace("/", " ")
        return os.path.join(self.get_album_dir(artist_name, album_title, album_release_year), f"{parsed_artist_name} - {parsed_album_title} - {parsed_track_number} {parsed_track_title}.mp3")

    def get_lidarr_album_dir(self, album):
        parsed_date = datetime.fromisoformat(album["releaseDate"].replace("Z", "+00:00"))
        album_year = parsed_date.year
        album_name = album["title"]
        album_str = album_name.replace("/", " ")
        album_folder = f"{album_str} ({album_year})"
        album_dir = os.path.join(album["artist"]["path"], album_folder)

        # tmp for local env
        album_dir = "/Users/michele/navidrome" + album_dir

        return album_dir



    def get_lidarr_track_file(self, album, track_title, track_number, disc_number):
        album_dir = self.get_lidarr_album_dir(album)
        artist_str = os.path.basename(album["artist"]['artistName'])
        album_name = album["title"]
        album_str = album_name.replace("/", " ")
        title_str = track_title.replace("/", " ")
        track_number = str(track_number).zfill(2)
        disc_number = str(disc_number).zfill(2)

        filename = f"{artist_str} - {album_str} - {disc_number} - {track_number} - {title_str}.{self.preferred_codec}"
        full_file_path = os.path.join(album_dir, filename)

        return full_file_path

