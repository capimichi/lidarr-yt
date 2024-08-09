import base64
import json
import os
from datetime import datetime

import eyed3
import ffmpeg
import requests
import yt_dlp
from eyed3 import AudioFile
from injector import inject
from mutagen.id3 import ID3, TIT2, TRCK, TPE1, TPE2, TALB, TYER, TCON
from pydub import AudioSegment

from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.helper.AudioHelper import AudioHelper
from lidarryt.helper.DownloadHelper import DownloadHelper
from lidarryt.helper.Eyed3Helper import Eyed3Helper
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from youtube_search import YoutubeSearch
from tqdm import tqdm
import tempfile

from lidarryt.helper.ShazamHelper import ShazamHelper
from lidarryt.helper.SongRecognizeHelper import SongRecognizeHelper
from lidarryt.helper.VideoSearchHelper import VideoSearchHelper
import logging

import asyncio
from shazamio import Shazam

from lidarryt.model.ShazamData import ShazamData


class DownloadService:
    lidarr_client: LidarrClient
    lidarr_fs_helper: LidarrFsHelper
    video_search_helper: VideoSearchHelper
    download_helper: DownloadHelper
    eyed3_helper: Eyed3Helper
    audio_helper: AudioHelper
    song_recognize_helper: SongRecognizeHelper

    @inject
    def __init__(self, lidarr_client: LidarrClient, lidarr_fs_helper: LidarrFsHelper,
                 video_search_helper: VideoSearchHelper,
                 download_helper: DownloadHelper, eyed3_helper: Eyed3Helper,
                 audio_helper: AudioHelper,
                    song_recognize_helper: SongRecognizeHelper
                 ):
        self.lidarr_client = lidarr_client
        self.lidarr_fs_helper = lidarr_fs_helper
        self.video_search_helper = video_search_helper
        self.download_helper = download_helper
        self.eyed3_helper = eyed3_helper
        self.audio_helper = audio_helper
        self.song_recognize_helper = song_recognize_helper

    def download(self):

        album_records = []
        missing_track_record_ids = []

        page = 1
        while True:
            missing_track_page = self.lidarr_client.get_missing_tracks(page=page, page_size=10)
            missing_track_page_records = missing_track_page['records']
            has_new = False

            for missing_track in missing_track_page_records:
                missing_track_id = missing_track['id']
                if missing_track_id not in missing_track_record_ids:
                    album_records.append(missing_track)
                    missing_track_record_ids.append(missing_track_id)
                    has_new = True

            page += 1
            if not has_new:
                break

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
            parsed_date = datetime.fromisoformat(album["releaseDate"].replace("Z", "+00:00"))
            album_year = parsed_date.year

            album_monitored = album['monitored']
            if not album_monitored:
                continue

            apple_album_data = self.video_search_helper.search_album_data(album_title, artist_name)
            apple_tracks = apple_album_data['tracks']

            tracks = self.lidarr_client.get_tracks(album_id=album_id)
            # for track in tqdm(tracks):
            track_index = -1
            for track in tracks:
                track_index += 1
                track_id = track['id']
                track_title = track['title']
                duration = track['duration']

                if (track_index >= len(apple_tracks)):
                    continue

                apple_track = apple_tracks[track_index]

                track_number = track_index + 1
                track['absoluteTrackNumber'] = track_number
                has_file = track['hasFile']

                if has_file:
                    continue

                album_dir = self.lidarr_fs_helper.get_lidarr_album_dir(album)
                if not os.path.exists(album_dir):
                    os.makedirs(album_dir)
                track_path = self.lidarr_fs_helper.get_lidarr_track_file(album, track)

                if(os.path.exists(track_path)):
                    continue

                logging.info(f"Downloading {artist_name} - {album_title} - {track_number} {track_title} from YouTube.")

                try:
                    apple_preview_url = apple_track['audio']['contentUrl']
                except Exception as e:
                    apple_preview_url = None

                if (not apple_preview_url):
                    continue

                apple_matched_item: ShazamData = self.song_recognize_helper.advanced_recognize_song_from_url(apple_preview_url, preferred_matches=3)
                if (not apple_matched_item or not apple_matched_item.has_track()):
                    continue

                apple_title = apple_matched_item.get_title()
                apple_album_title = apple_matched_item.get_album()

                try:
                    found_video_ids = self.video_search_helper.search_on_youtube_multi(track_title, album_title,
                                                                                       artist_name, duration)
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
                            logging.info(f"Trying with video id: '{found_video_id}'")
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

                                matched_data = self.song_recognize_helper.advanced_recognize_song(file_path, preferred_matches=3)
                                if(not matched_data or not matched_data.has_track()):
                                    os.remove(file_path)
                                    continue

                                is_right_file = matched_data.get_title() == apple_title

                                matched_album_title = matched_data.get_album()
                                if (matched_album_title != apple_album_title):
                                    is_right_file = False

                                if is_right_file:
                                    logging.info(f"Matched {artist_name} - {album_title} - {track_number} {track_title} with '{found_video_id}'")
                                    os.rename(file_path, track_path)

                if (os.path.exists(track_path)):
                    self.eyed3_helper.apply_track_metadata(track_path, track_title, track_number, artist_name,
                                                           album_title,
                                                           album_year, album, tracks)

            logging.info(f"Done downloading {artist_name} - {album_title}.")
