import json
import os

import eyed3
import ffmpeg
import yt_dlp
from injector import inject

from lidarryt.client import LastFmClient
from lidarryt.client.ItunesClient import ItunesClient
from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.client.OdesliClient import OdesliClient
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from youtube_search import YoutubeSearch
from tqdm import tqdm

class OdesliService:

    lidarr_client: LidarrClient
    odesli_client: OdesliClient
    itunes_client: ItunesClient
    lidarr_fs_helper: LidarrFsHelper
    audio_quality: int
    youtube_duration_threshold: int

    @inject
    def __init__(self, lidarr_client: LidarrClient, odesli_client: OdesliClient, itunes_client: ItunesClient, lidarr_fs_helper: LidarrFsHelper, audio_quality: int, youtube_duration_threshold: int):
        self.lidarr_client = lidarr_client
        self.odesli_client = odesli_client
        self.itunes_client = itunes_client
        self.lidarr_fs_helper = lidarr_fs_helper
        self.audio_quality = audio_quality
        self.youtube_duration_threshold = youtube_duration_threshold

    def update(self):

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

            tracks = self.lidarr_client.get_tracks(album_id=album_id)

            track_index = -1
            # for track in tqdm(tracks):
            for track in tracks:
                track_index += 1

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


                search_term = f"{track_title} - {album_title} - {artist_name}"

                search_data = self.itunes_client.search(search_term)
                found_track_id = None
                results = search_data['results']
                # filter out the results that have not wrapperType == 'track'
                results = [result for result in results if result['wrapperType'] == 'track']
                for result in results:
                    result_duration = result['trackTimeMillis']
                    duration_difference = abs(duration - result_duration) / 1000

                    if(duration_difference <= self.youtube_duration_threshold):
                        found_track_id = result['trackId']
                        break

                if not found_track_id:
                    continue

                found_video_id = self.odesli_client.get_track_youtube_id(found_track_id)

                if not found_video_id:
                    continue

                track_path_template = track_path.replace('.mp3', '.%(ext)s')
                video_id = found_video_id
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                options = {
                    'extract_audio': True,
                    'audio_format': 'mp3',
                    'audio_quality': self.audio_quality,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': str(self.audio_quality),
                    }],
                    'format': 'bestaudio',
                    # 'quiet': True,
                    # 'noprogress': True,
                    'outtmpl': track_path_template,
                }
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([video_url])

                # set metadata album
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