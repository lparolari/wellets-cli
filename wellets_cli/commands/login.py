from getpass import getpass
from typing import Optional

import click

import wellets_cli.api as api
from wellets_cli.auth import persist_auth


@click.command()
@click.option("--email")
@click.option("--password")
def login(email: Optional[str], password: Optional[str]):
    email = email or input("Email: ")
    password = password or getpass.getpass()

    user_session = api.login(email, password)

    persist_auth(user_session.json())
