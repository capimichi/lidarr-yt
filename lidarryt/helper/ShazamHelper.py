from shazamio import Shazam


class ShazamHelper:

    async def recognize_song(self, audio_file_path):
        shazam = Shazam()
        out = await shazam.recognize_song(audio_file_path)
        return out
