import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Wallet
from wellets_cli.util import change_value, get_currency_by_id, make_headers


@click.group()
def portfolio():
    pass
