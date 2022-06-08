import getpass
import json
from locale import currency
from pathlib import Path
from pprint import pprint
from typing import Optional

import click
import requests
from pydantic import ValidationError
from PyInquirer import prompt
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.api import get_currencies, get_wallets
from wellets_cli.auth import get_auth_token, get_email, persist_auth
from wellets_cli.model import Wallet
from wellets_cli.prompt import prompt_wallet
from wellets_cli.util import change_value, get_currency_by_id, make_headers


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

    user_session = api.login(email, password)

    persist_auth(user_session.json())


@click.command(name="list")
@click.option("--auth-token")
def list_wallets(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = get_currencies(headers=headers)
    wallets = get_wallets(headers=headers)
    base_currency = api.get_preferred_currency(headers=headers)

    def get_row_value(wallet: Wallet):
        currency = get_currency_by_id(currencies, wallet.currency_id)
        return {
            "id": wallet.id,
            "alias": wallet.alias,
            "currency": currency.acronym,
            "balance": wallet.balance,
            "countervalue": change_value(
                currency.dollar_rate, base_currency.dollar_rate, wallet.balance
            ),
            "created_at": wallet.created_at.strftime("%Y-%m-%d"),
        }

    data = list(map(get_row_value, wallets))

    print(tabulate(data, headers="keys"))


@click.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--currency-id")
def create_wallet(auth_token: str, alias: str, currency_id: str):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = get_currencies(headers=headers)

    questions = [
        *(
            []
            if alias
            else [
                {
                    "type": "input",
                    "name": "alias",
                    "message": "Alias",
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
                    "message": "Currency",
                    "choices": list(map(lambda x: x.acronym, currencies)),
                    "filter": lambda currency: list(
                        filter(lambda x: x.acronym == currency, currencies)
                    )[0].id,
                }
            ]
        ),
    ]

    data = prompt(questions)

    wallet = api.create_wallet(data, headers=headers)

    print(wallet.id)


@click.command(name="delete")
@click.option("--auth-token")
@click.option("--wallet-id")
def delete_wallet(auth_token, wallet_id):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)
    requires_interaction = wallet_id is None

    wallets = api.get_wallets(headers=headers)

    if requires_interaction:
        wallet_id = prompt_wallet(wallets)

    wallet = api.delete_wallet(
        wallet_id=wallet_id,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    print(wallet.id)


@click.command(name="average-load-price")
@click.option("--auth-token")
@click.option("--wallet-id")
def show_wallet_average_load_price(wallet_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)
    requires_interaction = wallet_id is None

    wallets = api.get_wallets(headers=headers)

    if requires_interaction:
        wallet_id = prompt_wallet(wallets)

    result = api.get_wallet_average_load_price(
        wallet_id=wallet_id,
        headers=headers,
    )

    print(f"{result.average_load_price} {result.base_currency.acronym}")


@click.command()
def whoami():
    email = get_email()

    if email:
        print(email)
    else:
        print("Not logged in")


def main():  # pragma: no cover
    wallet.add_command(list_wallets)
    wallet.add_command(create_wallet)
    wallet.add_command(delete_wallet)
    wallet.add_command(show_wallet_average_load_price)

    cli.add_command(wallet)
    cli.add_command(login)
    cli.add_command(whoami)

    cli()
