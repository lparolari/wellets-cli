import getpass
import json
from locale import currency
from typing import Optional

import click
import requests
from tabulate import tabulate

from wellets_cli.api import get_currencies, get_wallets
from wellets_cli.util import get_currency_acronym_by_id


@click.group()
def cli():
    pass


@click.group()
def wallet():
    pass


@click.command()
@click.option("--email")
@click.option("--password")
def login(email: Optional[str], password: Optional[str]):
    email = email or input("Email: ")
    password = password or getpass.getpass()

    response = requests.post(
        "http://localhost:3333/users/sessions",
        json={"email": email, "password": password},
    )

    if response.ok:
        print(response.json())
    else:
        raise ValueError(response)


@click.command(name="list")
@click.option("--auth-token")
def list_wallets(auth_token):
    currencies = get_currencies(
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    wallets = get_wallets(
        headers={"Authorization": f"Bearer {auth_token}"},
        params={"limit": 25, "page": 1},
    )

    data = map(
        lambda x: {
            "id": x.id,
            "balance": x.balance,
            "currency": get_currency_acronym_by_id(
                currencies, currency_id=x.currency_id
            ),
            "created_at": x.created_at.strftime("%Y-%m-%d"),
        },
        wallets,
    )
    print(tabulate(data, headers="keys"))


def main():  # pragma: no cover
    wallet.add_command(list_wallets)

    cli.add_command(wallet)
    cli.add_command(login)

    cli()
