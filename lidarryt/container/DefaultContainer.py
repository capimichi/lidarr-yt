import os

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

        last_fm_api_key = os.getenv('LASTFM_API_KEY')

        self.set(LidarrClient.__name__, LidarrClient(lidarr_base_url, lidarr_api_key))
        self.set(LastFmClient.__name__, LastFmClient(last_fm_api_key))
        self.set(ItunesClient.__name__, ItunesClient())
        self.set(OdesliClient.__name__, OdesliClient())
        self.set(AppleMusicClient.__name__, AppleMusicClient())

        self.set(ShazamHelper.__name__, ShazamHelper())
        self.set(LidarrFsHelper.__name__, LidarrFsHelper(lidarr_root_folder))
        self.set(DownloadHelper.__name__, DownloadHelper(youtube_audio_quality))
        self.set(VideoSearchHelper.__name__, VideoSearchHelper(
            self.get(ItunesClient.__name__),
            self.get(OdesliClient.__name__),
            self.get(AppleMusicClient.__name__),
            youtube_duration_threshold
        ))

        self.set(DownloadService.__name__, DownloadService(
            self.get(LidarrClient.__name__),
            self.get(LidarrFsHelper.__name__),
            self.get(VideoSearchHelper.__name__),
            self.get(DownloadHelper.__name__),
            self.get(ShazamHelper.__name__),
            youtube_audio_quality,
            youtube_duration_threshold
        ))

        self.set(LastFmService.__name__, LastFmService(
            self.get(LidarrClient.__name__),
            self.get(LastFmClient.__name__),
            self.get(LidarrFsHelper.__name__),
            youtube_audio_quality
        ))

        self.set(OdesliService.__name__, OdesliService(
            self.get(LidarrClient.__name__),
            self.get(OdesliClient.__name__),
            self.get(ItunesClient.__name__),
            self.get(LidarrFsHelper.__name__),
            youtube_audio_quality,
            youtube_duration_threshold
        ))


    @staticmethod
    def getInstance():
        if not DefaultContainer._instance:
            DefaultContainer._instance = DefaultContainer()
        return DefaultContainer._instance