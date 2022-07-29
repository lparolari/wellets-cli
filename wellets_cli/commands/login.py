from typing import Optional

import click
from InquirerPy import inquirer

import wellets_cli.api as api
from wellets_cli.auth import persist_auth
from wellets_cli.config import Config


@click.command()
@click.option("--email")
@click.option("--password")
def login(email: Optional[str], password: Optional[str]):
    email = (
        email
        or Config.api_username
        or inquirer.text(message="Email").execute()
    )
    password = (
        password
        or Config.api_password
        or inquirer.secret(message="Password").execute()
    )

    user_session = api.login(email, password)

    persist_auth(user_session.json())
