import getpass
import json
from locale import currency
from pprint import pprint
from typing import Optional

import click
import requests
from pydantic import ValidationError
from PyInquirer import prompt
from tabulate import tabulate

import wellets_cli.api as api
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
            "alias": x.alias,
            "balance": x.balance,
            "currency": get_currency_acronym_by_id(
                currencies, currency_id=x.currency_id
            ),
            "created_at": x.created_at.strftime("%Y-%m-%d"),
        },
        wallets,
    )
    print(tabulate(data, headers="keys"))


@click.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--currency-id")
def create_wallet(auth_token: str, alias: str, currency_id: str):
    currencies = get_currencies(
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    questions = [
        *(
            []
            if alias
            else [
                {
                    "type": "input",
                    "name": "alias",
                    "message": "Alias?",
                    "validate": lambda val: True
                    if val != ""
                    else "Cannot be empty",
                }
            ]
        ),
        *(
            []
            if currency_id
            else [
                {
                    "type": "list",
                    "name": "currency_id",
                    "message": "Currency?",
                    "choices": list(map(lambda x: x.acronym, currencies)),
                    "filter": lambda currency: list(
                        filter(lambda x: x.acronym == currency, currencies)
                    )[0].id,
                }
            ]
        ),
    ]

    answers = prompt(questions)

    print("Wallet")
    print(json.dumps(answers, indent=4))

    question = {
        "type": "confirm",
        "message": "Do you want to continue?",
        "name": "continue",
        "default": True,
    }

    prompt([question])

    wallet = api.create_wallet(answers, headers={"Authorization": f"Bearer {auth_token}"})

    print(wallet.id)


def main():  # pragma: no cover
    wallet.add_command(list_wallets)
    wallet.add_command(create_wallet)

    cli.add_command(wallet)
    cli.add_command(login)

    cli()
