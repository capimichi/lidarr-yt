import os

from youtube_search import YoutubeSearch


class VideoSearchHelper:

    def __init__(self, itunes_client, odesli_client, youtube_duration_threshold):
        self.itunes_client = itunes_client
        self.odesli_client = odesli_client
        self.youtube_duration_threshold = youtube_duration_threshold


    def search_on_youtube_multi(self, track_title, album_title, artist_name, duration):
        search_terms = [
            f"{track_title} {artist_name}",
            f"{track_title} - {album_title} - {artist_name}",
        ]

        found_video_ids = []
        for search_term in search_terms:

            youtube_results = YoutubeSearch(search_term, max_results=10)
            for video in youtube_results.videos:
                video_id = video['id']
                video_title = video['title']

                # avoid live versions
                # if ' live' in video_title.lower():
                #     continue

                video_duration_mm_ss = video['duration']
                video_duration_mm = int(video_duration_mm_ss.split(':')[0])
                video_duration_ss = int(video_duration_mm_ss.split(':')[1])
                video_duration_ms = (video_duration_mm * 60 + video_duration_ss) * 1000

                # skip if video duration is more than 20 minutes
                if video_duration_mm > 10:
                    continue

                duration_difference = abs(duration - video_duration_ms) / 1000
                # if (video_duration_ms <= 0 or duration_difference <= self.youtube_duration_threshold):
                found_video_ids.append({
                    'id': video_id,
                    'title': video_title,
                    'duration_difference': duration_difference
                })

        # if(duration > 0):
        #     found_video_ids = sorted(found_video_ids, key=lambda x: x['duration_difference'])
        def sort(x):
            title = x['title'].lower()
            # duration_difference = x['duration_difference']
            has_keywords = ('lyric' in title) or ('official' in title)
            has_keywords_value = 0 if has_keywords else 1
            return has_keywords_value
        found_video_ids = sorted(found_video_ids, key=sort)

        found_video_ids = [video['id'] for video in found_video_ids]

        unique_ids = []
        for video_id in found_video_ids:
            if video_id not in unique_ids:
                unique_ids.append(video_id)
        found_video_ids = unique_ids

        # make unique
        # found_video_ids = list(set(found_video_ids))

        return found_video_ids

    def search_on_youtube(self, track_title, album_title, artist_name, duration):
        ids = self.search_on_youtube_multi(track_title, album_title, artist_name, duration)
        if len(ids) > 0:
            return ids[0]
        return None

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