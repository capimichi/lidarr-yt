from lidarryt.model.AppleTrackData import AppleTrackData


class AppleAlbumData:

    data = None

    def __init__(self, data):
        self.data = data

    def get_tracks(self):
        data = self.data

        if(not "data" in data):
            return []

        data = data["data"]

        if(not "sections" in data):
            return []

        sections = data["sections"]

        tracks = []
        for section in sections:
            if(section['itemKind'] == 'trackLockup'):
                items = section['items']

                for item in items:
                    track = AppleTrackData(item)
                    tracks.append(track)

        return tracks

    def get_disc_count(self):
        tracks = self.get_tracks()
        max_disc_number = 0
        for track in tracks:
            disc_number = track.get_disc_number()
            if(disc_number > max_disc_number):
                max_disc_number = disc_number

        return max_disc_number