import os

from injector import Injector

from lidarryt.client.AppleMusicClient import AppleMusicClient
from lidarryt.client.ItunesClient import ItunesClient
from lidarryt.client.LastFmClient import LastFmClient
from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.client.OdesliClient import OdesliClient
from lidarryt.helper.DownloadHelper import DownloadHelper
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from lidarryt.helper.ShazamHelper import ShazamHelper
from lidarryt.helper.VideoSearchHelper import VideoSearchHelper
from lidarryt.service.DownloadService import DownloadService
from lidarryt.service.LastFmService import LastFmService
from lidarryt.service.OdesliService import OdesliService


class DefaultContainer:
    _instance = None
    _classes = {}
    _injector:Injector = None

    def set(self, key, value):
        self._classes[key] = value

    def get(self, key):
        return self._injector.get(key)

    def __init__(self):
        self._classes = {}

        lidarr_base_url = os.getenv('LIDARR_BASE_URL')
        lidarr_api_key = os.getenv('LIDARR_API_KEY')
        lidarr_root_folder = os.getenv('LIDARR_ROOT_FOLDER')

        youtube_audio_quality = int(os.getenv('YOUTUBE_AUDIO_QUALITY'))
        enable_proxy = os.getenv('ENABLE_PROXY') == "true"

        last_fm_api_key = os.getenv('LASTFM_API_KEY')

        self._injector = Injector()

        self._injector.binder.bind(LidarrClient, LidarrClient(lidarr_base_url, lidarr_api_key))
        self._injector.binder.bind(LastFmClient, LastFmClient(last_fm_api_key))
        self._injector.binder.bind(LidarrFsHelper, LidarrFsHelper(lidarr_root_folder))
        self._injector.binder.bind(DownloadHelper, DownloadHelper(youtube_audio_quality, enable_proxy))



    @staticmethod
    def getInstance():
        if not DefaultContainer._instance:
            DefaultContainer._instance = DefaultContainer()
        return DefaultContainer._instance