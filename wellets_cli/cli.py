import click

from wellets_cli.commands.accumulation import accumulation
from wellets_cli.commands.asset import asset
from wellets_cli.commands.config import config
from wellets_cli.commands.currency import currency
from wellets_cli.commands.login import login
from wellets_cli.commands.portfolio import portfolio
from wellets_cli.commands.register import register
from wellets_cli.commands.transaction import transaction
from wellets_cli.commands.transfer import transfer
from wellets_cli.commands.wallet import wallet
from wellets_cli.commands.whoami import whoami


@click.group()
def cli():
    pass


def main():  # pragma: no cover
    cli.add_command(wallet)
    cli.add_command(login)
    cli.add_command(whoami)
    cli.add_command(portfolio)
    cli.add_command(config)
    cli.add_command(transaction)
    cli.add_command(currency)
    cli.add_command(accumulation)
    cli.add_command(transfer)
    cli.add_command(asset)
    cli.add_command(register)

    cli()
