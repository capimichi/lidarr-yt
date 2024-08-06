import os


class FfmpegHelper:

    ffmpeg_path: str = None

    def __init__(self, ffmpeg_path):
        self.ffmpeg_path = ffmpeg_path


    def reduce_audio_quality(self, input_file, output_file):
        #ffmpeg -i in.mp3 -b:a 96k -map a out.mp3

        input_file_parsed = input_file
        output_file_parsed = output_file

        command = f"{self.ffmpeg_path} -i \"{input_file_parsed}\" -b:a 96k -map a \"{output_file_parsed}\""
        os.system(command)
