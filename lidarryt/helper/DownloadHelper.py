import os

import eyed3
import yt_dlp
from injector import inject
from youtube_search import YoutubeSearch
from fp.fp import FreeProxy


class DownloadHelper:

    audio_quality = 5
    enable_proxy = False

    @inject
    def __init__(self, audio_quality, enable_proxy):
        self.audio_quality = audio_quality
        self.enable_proxy = enable_proxy

    def download_multiple_video(self, ids, dir):
        urls = [f"https://www.youtube.com/watch?v={id}" for id in ids]
        track_path_template = "%(timestamp)s.%(ext)s"
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
        if(self.enable_proxy):
            options['proxy'] = FreeProxy(rand=True, anonym=True, timeout=5).get()

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

