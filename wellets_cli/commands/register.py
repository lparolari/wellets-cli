from typing import Optional

import click
from InquirerPy import inquirer

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.util import make_headers
from wellets_cli.validator import (
    AndValidator,
    EmailValidator,
    EmptyInputValidator,
    PasswordMatchValidator,
    TextLengthValidator,
)


@click.command()
@click.option("--email")
@click.option("--password")
@click.option("--auth-token")
def register(email: Optional[str], password: Optional[str], auth_token: Optional[str]):
    """
    Register a new Wellets account.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    email = (
        email
        or inquirer.text(
            message="Email",
            validate=AndValidator([EmptyInputValidator(), EmailValidator()]),
        ).execute()
    )
    password = (
        password
        or inquirer.secret(
            message="Password",
            validate=AndValidator([EmptyInputValidator(), TextLengthValidator(6)]),
        ).execute()
    )

    inquirer.secret(
        message="Confirm password",
        validate=AndValidator(
            [
                EmptyInputValidator(),
                TextLengthValidator(6),
                PasswordMatchValidator(password),
            ]
        ),
    ).execute()

    user = api.register(data={"email": email, "password": password}, headers=headers)

    print(user.id)
