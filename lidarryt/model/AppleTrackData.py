

class AppleTrackData:

    data = None

    def __init__(self, data):
        self.data = data


    def get_disc_number(self):
        data = self.data
        if(not "discNumber" in data):
            return 1
        return data['discNumber']

    def get_track_number(self):
        data = self.data
        if(not "trackNumber" in data):
            return 1
        return data['trackNumber']

    def get_title(self):
        data = self.data
        if(not "title" in data):
            return ""
        return data['title']

    def get_duration(self):
        data = self.data
        if(not "duration" in data):
            return 0
        return data['duration']

    def get_artist_name(self):
        data = self.data
        if(not "artistName" in data):
            return ""
        return data['artistName']

    def get_preview_url(self):
        data = self.data
        if(not "previewUrl" in data):
            return ""
        return data['previewUrl']