import asyncio
import os
import tempfile
import time
from math import floor
from typing import Optional

import requests
from injector import inject
from shazamio import Shazam

from lidarryt.helper.AudioHelper import AudioHelper
from lidarryt.helper.ShazamHelper import ShazamHelper
from lidarryt.model.ShazamData import ShazamData


class SongRecognizeHelper:

    audio_helper: AudioHelper
    shazam_helper: ShazamHelper

    @inject
    def __init__(self, audio_helper: AudioHelper, shazam_helper: ShazamHelper):
        self.audio_helper = audio_helper
        self.shazam_helper = shazam_helper

    def advanced_recognize_song_from_url(self, audio_url, preferred_matches=5, delay=500) -> Optional[ShazamData]:
        tmp_path = tempfile.mktemp()

        apple_preview_response = requests.get(audio_url)
        with open(tmp_path, 'wb') as f:
            f.write(apple_preview_response.content)

        data = self.advanced_recognize_song(tmp_path, preferred_matches=preferred_matches, delay=delay)
        os.remove(tmp_path)

        return data

    def advanced_recognize_song(self, audio_file_path, preferred_matches=5, delay=500) -> Optional[ShazamData]:
        # get the length of the file, split it by preferred_matches, but at least every 10 seconds, then for each part, recognize the song title, make a statistics of the most frequent title and keep it

        audio_length = self.audio_helper.get_audio_length(audio_file_path)

        while ((audio_length / preferred_matches) < 10000):
            preferred_matches -= 1

        cut_length = floor(audio_length / preferred_matches)

        split_parts = [
            (0, floor(audio_length)),
            (0, floor(cut_length / 2)),
            (floor(cut_length / 2), floor(cut_length)),
        ]

        recognized_songs = []
        for i in range(0, preferred_matches):
            split_parts.append((i * cut_length, (i + 1) * cut_length))

        for split_part in split_parts:
            split_part_str = f"{split_part[0]}-{split_part[1]}"
            audio_tmp_path_i = audio_file_path + f"_{split_part_str}"
            self.audio_helper.cut_audio(audio_file_path, audio_tmp_path_i, split_part[0], split_part[1])
            # recognized_song_data = asyncio.run(self.shazam_helper.recognize_song(audio_tmp_path_i))
            # wait for delay
            time.sleep(delay / 1000)
            try:
                recognized_song_data = asyncio.run(
                    asyncio.wait_for(self.shazam_helper.recognize_song(audio_tmp_path_i), timeout=15)
                )
            except asyncio.TimeoutError:
                continue
            recognized_song = ShazamData(recognized_song_data)
            if (recognized_song.has_track()):
                recognized_songs.append(recognized_song)
            os.remove(audio_tmp_path_i)

        most_frequent_titles = {}
        for recognized_song in recognized_songs:
            recognized_song_title = recognized_song.get_title()
            if recognized_song_title not in most_frequent_titles:
                most_frequent_titles[recognized_song_title] = 0
            most_frequent_titles[recognized_song_title] += 1

        if(len(most_frequent_titles) == 0):
            return None

        most_frequent_titles_sorted = sorted(most_frequent_titles.items(), key=lambda x: x[1], reverse=True)

        most_frequent_title = most_frequent_titles_sorted[0][0]

        for recognized_song in recognized_songs:
            if recognized_song.get_title() == most_frequent_title:
                return recognized_song

        return None