import click

from wellets_cli.commands.config import config
from wellets_cli.commands.login import login
from wellets_cli.commands.portfolio import portfolio
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

    cli()
