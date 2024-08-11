# start dockerfile from python image
FROM python:3.10

# install ffmpeg and ffprobe
RUN apt-get update && apt-get install -y ffmpeg

# set working directory
WORKDIR /app

# copy the current directory contents into the container at /app
COPY . /app

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# run python cron.py
CMD ["python3", "cron.py"]