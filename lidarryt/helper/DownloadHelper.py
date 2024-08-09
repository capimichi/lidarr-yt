import os

import eyed3
import yt_dlp
from injector import inject
from youtube_search import YoutubeSearch


class DownloadHelper:

    audio_quality = 5

    @inject
    def __init__(self, audio_quality):
        self.audio_quality = audio_quality

    def download_multiple_video(self, ids, dir):
        urls = [f"https://www.youtube.com/watch?v={id}" for id in ids]
        track_path_template = "%(id)s.%(ext)s"
        track_path_template = os.path.join(dir, track_path_template)
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
            ydl.download(
                urls
            )

    def download_video(self, id, path):
        track_path_template = path.replace('.mp3', '.%(ext)s')

        video_url = f"https://www.youtube.com/watch?v={id}"
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

