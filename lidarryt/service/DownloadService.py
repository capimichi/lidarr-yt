import json
import os

import eyed3
import ffmpeg
import yt_dlp

from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.helper.DownloadHelper import DownloadHelper
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from youtube_search import YoutubeSearch
from tqdm import tqdm

from lidarryt.helper.VideoSearchHelper import VideoSearchHelper


class DownloadService:

    lidarr_client: LidarrClient
    lidarr_fs_helper: LidarrFsHelper
    video_search_helper: VideoSearchHelper
    download_helper: DownloadHelper
    audio_quality: int
    duration_threshold: int

    def __init__(self, lidarr_client: LidarrClient, lidarr_fs_helper: LidarrFsHelper, video_search_helper: VideoSearchHelper, download_helper: DownloadHelper, audio_quality: int, duration_threshold: int):
        self.lidarr_client = lidarr_client
        self.lidarr_fs_helper = lidarr_fs_helper
        self.video_search_helper = video_search_helper
        self.download_helper = download_helper
        self.audio_quality = audio_quality
        self.duration_threshold = duration_threshold

    def download(self):

        missing_tracks = self.lidarr_client.get_missing_tracks()
        album_records = missing_tracks['records']

        for album in album_records:
            album_id = album['id']
            album_title = album['title']
            artist_id = album['artistId']

            artist = self.lidarr_client.get_artist(artist_id)
            artist_name = artist['artistName']

            album = self.lidarr_client.get_album(album_id)
            album_release_date = album['releaseDate']
            album_release_year = album_release_date.split('-')[0]

            # album_dir = self.lidarr_fs_helper.get_album_dir(artist_name, album_title, album_release_year)

            tracks = self.lidarr_client.get_tracks(album_id=album_id)
            # for track in tqdm(tracks):
            for track in tracks:
                track_title = track['title']
                duration = track['duration']
                track_number = track['trackNumber']
                # remove letters from track number
                track_number = int(''.join(filter(str.isdigit, track_number)))
                disc_number = track['mediumNumber']

                album_dir = self.lidarr_fs_helper.get_album_dir(artist_name, album_title, album_release_year)
                if not os.path.exists(album_dir):
                    os.makedirs(album_dir)
                track_path = self.lidarr_fs_helper.get_track_file(artist_name, album_title, album_release_year,
                                                                  track_title, disc_number, track_number)

                if(os.path.exists(track_path)):
                    audiofile = eyed3.load(track_path)
                    if(
                            audiofile.tag.artist == artist_name
                            and audiofile.tag.album == album_title
                            and audiofile.tag.title == track_title
                    ):
                        # print(f"Skipping {artist_name} - {album_title} - {track_number} {track_title} as it already exists.")
                        continue

                try:
                    found_video_id = self.video_search_helper.search_on_odesli(track_title, album_title, artist_name, duration)
                except Exception as e:
                    found_video_id = None

                if(found_video_id):
                    try:
                        self.download_helper.download_video(found_video_id, track_path)
                    except Exception as e:
                        pass

                if(not os.path.exists(track_path)):
                    try:
                        found_video_id = self.video_search_helper.search_on_youtube(track_title, album_title, artist_name, duration)
                    except Exception as e:
                        found_video_id = None

                    if(found_video_id):
                        try:
                            self.download_helper.download_video(found_video_id, track_path)
                        except Exception as e:
                            pass

                if (os.path.exists(track_path)):
                    audiofile = eyed3.load(track_path)
                    audiofile.tag.artist = artist_name
                    audiofile.tag.album = album_title
                    audiofile.tag.album_artist = artist_name
                    audiofile.tag.title = track_title
                    audiofile.tag.track_num = track_number
                    audiofile.tag.disc_num = disc_number
                    audiofile.tag.release_date = album_release_date

                    audiofile.tag.save()

                # print(f"Downloaded {artist_name} - {album_title} - {track_number} {track_title} from YouTube.")