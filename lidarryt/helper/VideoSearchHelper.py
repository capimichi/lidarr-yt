import os

from youtube_search import YoutubeSearch


class VideoSearchHelper:

    def __init__(self, itunes_client, odesli_client, youtube_duration_threshold):
        self.itunes_client = itunes_client
        self.odesli_client = odesli_client
        self.youtube_duration_threshold = youtube_duration_threshold


    def search_on_youtube(self, track_title, album_title, artist_name, duration):
        search_term = f"{track_title} - {album_title} - {artist_name}"

        found_video_id = None

        youtube_results = YoutubeSearch(search_term, max_results=10)
        for video in youtube_results.videos:
            video_id = video['id']
            video_title = video['title']

            # avoid live versions
            if 'live' in video_title.lower():
                continue

            video_duration_mm_ss = video['duration']
            video_duration_mm = int(video_duration_mm_ss.split(':')[0])
            video_duration_ss = int(video_duration_mm_ss.split(':')[1])
            video_duration_ms = (video_duration_mm * 60 + video_duration_ss) * 1000

            duration_difference = abs(duration - video_duration_ms) / 1000

            if (duration_difference <= self.youtube_duration_threshold):
                found_video_id = video_id
                break

        if not found_video_id:
            return None

        return found_video_id

    def search_on_odesli(self, track_title, album_title, artist_name, duration):
        search_term = f"{track_title} - {album_title} - {artist_name}"

        search_data = self.itunes_client.search(search_term)
        found_track_id = None
        results = search_data['results']
        # filter out the results that have not wrapperType == 'track'
        results = [result for result in results if result['wrapperType'] == 'track']
        for result in results:
            result_duration = result['trackTimeMillis']
            duration_difference = abs(duration - result_duration) / 1000

            if (duration_difference <= self.youtube_duration_threshold):
                found_track_id = result['trackId']
                break

        if not found_track_id:
            return None

        found_video_id = self.odesli_client.get_track_youtube_id(found_track_id)

        if not found_video_id:
            return None

        return found_video_id