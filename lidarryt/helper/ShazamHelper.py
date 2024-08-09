import os
import tempfile
from typing import Optional

import requests
from injector import inject
from shazamio import Shazam

from lidarryt.helper.AudioHelper import AudioHelper
from lidarryt.model.ShazamData import ShazamData


class ShazamHelper:

    audio_helper: AudioHelper

    @inject
    def __init__(self, audio_helper: AudioHelper):
        self.audio_helper = audio_helper

    async def recognize_song(self, audio_file_path):
        shazam = Shazam()
        out = await shazam.recognize_song(audio_file_path)
        return out