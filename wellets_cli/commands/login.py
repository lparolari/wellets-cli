from typing import Optional

import click
from InquirerPy import inquirer

import wellets_cli.api as api
from wellets_cli.auth import persist_auth
from wellets_cli.config import settings


@click.command()
@click.option("--email")
@click.option("--password")
def login(email: Optional[str], password: Optional[str]):
    """
    Login with your Wellets credentials.
    """
    email = (
        email
        or settings.get("api_username")
        or inquirer.text(message="Email").execute()
    )
    password = (
        password
        or settings.get("api_password")
        or inquirer.secret(message="Password").execute()
    )

    user_session = api.login(email, password)

    persist_auth(user_session.json())
