import click
from dotenv import load_dotenv

from lidarryt.container.DefaultContainer import DefaultContainer
from lidarryt.service.DownloadService import DownloadService

load_dotenv()

default_container = DefaultContainer.getInstance()

@click.group()
def cli():
    pass

@cli.command()
def download():
    download_service: DownloadService = default_container.get(DownloadService.__name__)
    download_service.download()

@cli.command()
def test():
    click.echo('Test command is executed.')

if __name__ == '__main__':
    cli()