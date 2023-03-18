from typing import Optional

import click
from InquirerPy import inquirer

import wellets_cli.api as api
from wellets_cli.auth import persist_auth
from wellets_cli.config import ConfigManager


@click.command()
@click.option("--email")
@click.option("--password")
def login(email: Optional[str], password: Optional[str]):
    email = (
        email
        or ConfigManager.get("api.username", throw=False)
        or inquirer.text(message="Email").execute()
    )
    password = (
        password
        or ConfigManager.get("api.password", throw=False)
        or inquirer.secret(message="Password").execute()
    )

    user_session = api.login(email, password)

    persist_auth(user_session.json())
