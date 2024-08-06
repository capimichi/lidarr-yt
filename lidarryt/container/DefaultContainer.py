import os

from lidarryt.client.LidarrClient import LidarrClient
from lidarryt.helper.FfmpegHelper import FfmpegHelper
from lidarryt.helper.LidarrFsHelper import LidarrFsHelper
from lidarryt.service.DownloadService import DownloadService


class DefaultContainer:
    _instance = None
    _classes = {}

    def set(self, key, value):
        self._classes[key] = value

    def get(self, key):
        return self._classes.get(key)

    def __init__(self):
        self._classes = {}

        lidarr_base_url = os.getenv('LIDARR_BASE_URL')
        lidarr_api_key = os.getenv('LIDARR_API_KEY')
        lidarr_root_folder = os.getenv('LIDARR_ROOT_FOLDER')


        youtube_duration_threshold = int(os.getenv('YOUTUBE_DURATION_THRESHOLD'))
        youtube_audio_quality = int(os.getenv('YOUTUBE_AUDIO_QUALITY'))

        self.set(LidarrClient.__name__, LidarrClient(lidarr_base_url, lidarr_api_key))

        self.set(LidarrFsHelper.__name__, LidarrFsHelper(lidarr_root_folder))

        self.set(DownloadService.__name__, DownloadService(
            self.get(LidarrClient.__name__),
            self.get(LidarrFsHelper.__name__),
            youtube_audio_quality,
            youtube_duration_threshold
        ))


    @staticmethod
    def getInstance():
        if not DefaultContainer._instance:
            DefaultContainer._instance = DefaultContainer()
        return DefaultContainer._instance