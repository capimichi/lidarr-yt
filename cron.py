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

    # lock_path = "download.lock"
    # check if download.lock is older than 10 minutes, if so, remove it
    # if os.path.exists(lock_path):
    #     if (time.time() - os.path.getmtime(lock_path)) > 600:
    #         os.remove(lock_path)

    # lock = fasteners.InterProcessLock(lock_path)
    try:
        # if(lock.acquire(blocking=False)):
        download_service: DownloadService = default_container.get(DownloadService)
        download_service.download()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    # finally:
    #     lock.release()

schedule.every().minute.do(download_job)

while 1:
    schedule.run_pending()
    time.sleep(1)
