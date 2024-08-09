from pydub import AudioSegment
from shazamio import Shazam


class AudioHelper:


    def get_audio_length(self, audio_file):
        """
        Get the length of an audio file in milliseconds.

        Args:
            audio_file (str): Path to the audio file.

        Returns:
            int: Length of the audio file in milliseconds.
        """
        # Load the audio file
        audio = AudioSegment.from_file(audio_file)

        # Get the length of the audio file
        return len(audio)

    def cut_audio(self, input_file, output_file, start_time, end_time):
        """
        Cut parts of an audio file and save it to a new file.

        Args:
            input_file (str): Path to the input audio file.
            output_file (str): Path to save the output audio file.
            start_time (int): Start time in milliseconds.
            end_time (int): End time in milliseconds.
        """
        # Load the audio file
        audio = AudioSegment.from_file(input_file)

        # Cut the audio
        cut_audio = audio[start_time:end_time]

        # Save the cut audio to a new file
        cut_audio.export(output_file, format="mp3")