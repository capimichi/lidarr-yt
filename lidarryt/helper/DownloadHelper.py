import logging
import os

import eyed3
import yt_dlp
from injector import inject
from youtube_search import YoutubeSearch
from fp.fp import FreeProxy


class DownloadHelper:

    audio_quality = 5
    enable_proxy = False

    current_proxy = None

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
            if(self.current_proxy):
                self.check_proxy(urls, options)

            while self.current_proxy is None:
                self.current_proxy = FreeProxy(rand=True, anonym=True, timeout=5).get()
                self.check_proxy(urls, options)

            options['proxy'] = self.current_proxy

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

    def check_proxy(self, urls, options):
        check_options = options.copy()
        check_options['proxy'] = self.current_proxy
        try:
            with yt_dlp.YoutubeDL(check_options) as ydl:
                ydl.download(
                    urls
                )
        except Exception as e:
            error_message = str(e)
            if("network error" in error_message.lower()):
                self.current_proxy = None
                logging.error(f"Proxy failed: {e}")
            if("not a bot" in error_message.lower()):
                self.current_proxy = None
                logging.error(f"Proxy failed: {e}")
