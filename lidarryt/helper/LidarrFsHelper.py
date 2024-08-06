import os


class LidarrFsHelper:

    root_folder : str = None

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
        return os.path.join(self.get_album_dir(artist_name, album_title, album_release_year), f"{parsed_artist_name} - {parsed_album_title} - {parsed_disc_number} - {parsed_track_number} {parsed_track_title}.mp3")