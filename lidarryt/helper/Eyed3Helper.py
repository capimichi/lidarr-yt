import eyed3
from eyed3 import AudioFile
from mutagen.id3 import ID3
from mutagen.id3 import ID3, TIT2, TRCK, TPE1, TPE2, TALB, TYER, TCON

class Eyed3Helper:

    def apply_track_metadata(self, track_path, track_title, track_number, artist_name, album_title, album_year, album, tracks):
        metadata = ID3(track_path)
        metadata.add(TIT2(encoding=3, text=track_title))
        metadata.add(TRCK(encoding=3, text=str(track_number)))
        metadata.add(TPE1(encoding=3, text=artist_name))
        metadata.add(TPE2(encoding=3, text=artist_name))
        metadata.add(TALB(encoding=3, text=album_title))
        metadata.add(TYER(encoding=3, text=str(album_year)))
        metadata.add(TCON(encoding=3, text=str(", ".join(album["genres"]))))

        # set total tracks
        metadata.save()

        audiofile: AudioFile = eyed3.load(track_path)
        audiofile.tag.track_num = (track_number, len(tracks))
        # set disc 1 of 1
        audiofile.tag.disc_num = (1, 1)
        audiofile.tag.save()