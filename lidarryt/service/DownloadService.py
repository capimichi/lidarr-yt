import base64
import json
import os

import eyed3
import ffmpeg
import requests
import yt_dlp

from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.helper.DownloadHelper import DownloadHelper
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from youtube_search import YoutubeSearch
from tqdm import tqdm
import tempfile

from lidarryt.helper.ShazamHelper import ShazamHelper
from lidarryt.helper.VideoSearchHelper import VideoSearchHelper
import logging

import asyncio
from shazamio import Shazam


class DownloadService:

    lidarr_client: LidarrClient
    lidarr_fs_helper: LidarrFsHelper
    video_search_helper: VideoSearchHelper
    download_helper: DownloadHelper
    shazam_helper: ShazamHelper
    audio_quality: int
    duration_threshold: int

    def __init__(self, lidarr_client: LidarrClient, lidarr_fs_helper: LidarrFsHelper, video_search_helper: VideoSearchHelper, download_helper: DownloadHelper, shazam_helper: ShazamHelper, audio_quality: int, duration_threshold: int):
        self.lidarr_client = lidarr_client
        self.lidarr_fs_helper = lidarr_fs_helper
        self.video_search_helper = video_search_helper
        self.download_helper = download_helper
        self.shazam_helper = shazam_helper
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

            has_yt_tag = False
            artist_tag_ids = artist['tags']
            for tag_id in artist_tag_ids:
                tag = self.lidarr_client.get_tag(tag_id)
                tag_label = tag['label']
                if tag_label == 'ytdl':
                    has_yt_tag = True

            if not has_yt_tag:
                continue


            album = self.lidarr_client.get_album(album_id)
            album_release_date = album['releaseDate']
            album_release_year = album_release_date.split('-')[0]

            album_monitored = album['monitored']
            if not album_monitored:
                continue

            # album_dir = self.lidarr_fs_helper.get_album_dir(artist_name, album_title, album_release_year)

            tracks = self.lidarr_client.get_tracks(album_id=album_id)
            # for track in tqdm(tracks):
            for track in tracks:
                track_title = track['title']
                duration = track['duration']
                # track_number = track['trackNumber']
                track_number = track['absoluteTrackNumber']
                has_file = track['hasFile']

                if has_file:
                    continue

                # remove letters from track number
                # track_number = int(''.join(filter(str.isdigit, track_number)))
                disc_number = track['mediumNumber']

                album_dir = self.lidarr_fs_helper.get_album_dir(artist_name, album_title, album_release_year)
                if not os.path.exists(album_dir):
                    os.makedirs(album_dir)
                track_path = self.lidarr_fs_helper.get_track_file(artist_name, album_title, album_release_year,
                                                                  track_title, disc_number, track_number)

                logging.info(f"Downloading {artist_name} - {album_title} - {track_number} {track_title} from YouTube.")

                # first let's search the song on odesli
                try:
                    apple_preview_url = self.video_search_helper.search_apple_preview_on_odesli(track_title, album_title, artist_name, duration)
                except Exception as e:
                    apple_preview_url = None

                if(not apple_preview_url):
                    continue

                apple_tmp_path = tempfile.mktemp()
                apple_preview_response = requests.get(apple_preview_url)
                with open(apple_tmp_path, 'wb') as f:
                    f.write(apple_preview_response.content)

                apple_matched_data = asyncio.run(self.shazam_helper.recognize_song(apple_tmp_path))
                if(not "track" in apple_matched_data):
                    continue

                os.remove(apple_tmp_path)

                apple_matched_track = apple_matched_data['track']
                apple_sections = apple_matched_track['sections']
                apple_album_title = ""
                apple_title = apple_matched_track['title']
                for section in apple_sections:
                    if(section['type'] == 'SONG'):
                        metadata_items = section['metadata']
                        for metadata_item in metadata_items:
                            metadata_title = metadata_item['title']
                            metadata_text = metadata_item['text']
                            if(metadata_title == 'Album'):
                                apple_album_title = metadata_text

                try:
                    found_video_ids = self.video_search_helper.search_on_youtube_multi(track_title, album_title, artist_name, duration)
                except Exception as e:
                    found_video_ids = []

                # tmpdirname = "/Users/michele/PycharmProjects/lidarr-yt/var/tmp"
                with tempfile.TemporaryDirectory() as tmpdirname:
                    for found_video_id in found_video_ids:
                        if (os.path.exists(track_path)):
                            break

                        for file in os.listdir(tmpdirname):
                            os.remove(os.path.join(tmpdirname, file))

                        try:
                            self.download_helper.download_multiple_video([found_video_id], tmpdirname)
                        except yt_dlp.DownloadError as e:
                            continue

                        # loop through downloaded files
                        for file in os.listdir(tmpdirname):
                            if file.endswith(".mp3"):

                                file_path = os.path.join(tmpdirname, file)

                                if os.path.exists(track_path):
                                    os.remove(file_path)
                                    continue

                                matched_data = asyncio.run(self.shazam_helper.recognize_song(file_path))
                                if("track" in matched_data):
                                    matched_track = matched_data['track']
                                else:
                                    os.remove(file_path)
                                    continue

                                sections = matched_track['sections']

                                is_right_file = matched_track['title'] == apple_title

                                for section in sections:
                                    if(section['type'] == 'SONG'):
                                        metadata_items = section['metadata']
                                        for metadata_item in metadata_items:
                                            metadata_title = metadata_item['title']
                                            metadata_text = metadata_item['text']

                                            if(metadata_title == 'Album'):
                                                if(metadata_text != apple_album_title):
                                                    is_right_file = False
                                                    break

                                if is_right_file:
                                    os.rename(file_path, track_path)


                if (os.path.exists(track_path)):
                    audiofile = eyed3.load(track_path)
                    audiofile.tag.artist = artist_name
                    audiofile.tag.album = album_title
                    audiofile.tag.album_artist = artist_name
                    audiofile.tag.title = track_title
                    audiofile.tag.track_num = track_number
                    # audiofile.tag.total_tracks = len(tracks)
                    # audiofile.tag.disc_num = disc_number
                    # audiofile.tag.release_date = album_release_date


                    audiofile.tag.save()
                    # print(f"Downloaded {artist_name} - {album_title} - {track_number} {track_title} from YouTube.")