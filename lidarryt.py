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

@click.group()
def cli():
    pass

@cli.command()
def download():
    download_service: DownloadService = default_container.get(DownloadService.__name__)
    download_service.download()

@cli.command()
def last_fm_update():
    last_fm_service: LastFmService = default_container.get(LastFmService.__name__)
    last_fm_service.update()

@cli.command()
def odesli_update():
    odesli_service: OdesliService = default_container.get(OdesliService.__name__)
    odesli_service.update()

@cli.command()
def test():
    click.echo('Test command is executed.')

if __name__ == '__main__':
    cli()