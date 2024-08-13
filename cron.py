import fasteners
import schedule
import time
import os

import click
from dotenv import load_dotenv

from lidarryt.container.DefaultContainer import DefaultContainer
from lidarryt.service.DownloadService import DownloadService
from lidarryt.service.LastFmService import LastFmService
from lidarryt.service.OdesliService import OdesliService

load_dotenv()

import logging

if(not os.path.exists("var/log")):
    os.makedirs("var/log")
logging.basicConfig(
    filename="var/log/app.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M",
)


default_container = DefaultContainer.getInstance()

def download_job():
    try:
        # if(lock.acquire(blocking=False)):
        download_service: DownloadService = default_container.get(DownloadService)
        download_service.download()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

schedule.every().hour.do(download_job)

while 1:
    schedule.run_pending()
    time.sleep(1)
