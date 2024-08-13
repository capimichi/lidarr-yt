import os

import eyed3
import yt_dlp
from injector import inject
from youtube_search import YoutubeSearch


class ProxyHelper:

    enable_proxy = False
    proxy: str = None

    @inject
    def __init__(self, enable_proxy, proxy):
        self.enable_proxy = enable_proxy
        self.proxy = proxy

    def is_proxy_enabled(self):
        return self.enable_proxy

    def get_proxy(self):
        return self.proxy