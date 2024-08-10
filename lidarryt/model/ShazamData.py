

class ShazamData:

    data = None

    def __init__(self, data):
        self.data = data

    def has_track(self):
        return "track" in self.data

    def get_title(self):
        data = self.data
        return data['track']['title']

    def get_subtitle(self):
        data = self.data
        return data['track']['subtitle']

    def get_album(self):
        data = self.data
        sections = data['track']['sections']
        for section in sections:
            if section['type'] == 'SONG':
                metadata_items = section['metadata']
                for metadata_item in metadata_items:
                    if metadata_item['title'] == 'Album':
                        return metadata_item['text']
        return ""