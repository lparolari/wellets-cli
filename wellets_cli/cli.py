import pathlib

import click

from wellets_cli.api import APIError
from wellets_cli.commands.accumulation import accumulation
from wellets_cli.commands.asset import asset
from wellets_cli.commands.currency import currency
from wellets_cli.commands.investment import investment
from wellets_cli.commands.login import login
from wellets_cli.commands.portfolio import portfolio
from wellets_cli.commands.register import register
from wellets_cli.commands.transaction import transaction
from wellets_cli.commands.transfer import transfer
from wellets_cli.commands.wallet import wallet
from wellets_cli.commands.whoami import whoami

try:
    VERSION_PATH = pathlib.Path(__file__).parent / "VERSION"
    VERSION = open(VERSION_PATH).read().strip()
except:
    VERSION = "unknown"


@click.group()
@click.version_option(VERSION)
def cli():
    pass


def main():  # pragma: no cover
    # user
    cli.add_command(login)
    cli.add_command(register)
    cli.add_command(whoami)

    # wallets and transactions
    cli.add_command(wallet)
    cli.add_command(transaction)
    cli.add_command(transfer)

    # assets
    cli.add_command(asset)
    cli.add_command(portfolio)

    # currency
    cli.add_command(currency)

    cli.add_command(accumulation)  # DEPRECATED
    cli.add_command(investment)  # PREVIEW

    try:
        cli()
    except APIError as e:
        error = click.style("ERROR", fg="red")
        click.echo(f"{error}: {e}")
        exit(1)
