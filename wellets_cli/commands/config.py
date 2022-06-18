import json

import click

from wellets_cli.config import Config


@click.group()
def config():
    pass


@config.command()
def show():
    print(json.dumps({"api_url": Config.api_url}, indent=4))
