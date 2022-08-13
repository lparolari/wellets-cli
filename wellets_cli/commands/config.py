import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.config import Config
from wellets_cli.util import make_headers

from ..question import currency_question


@click.group()
def config():
    pass


@config.command()
@click.option("--auth-token")
def show(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    preferred_currency = api.get_preferred_currency(headers=headers)

    data = [
        {"config": "api_url", "value": Config.api_url},
        {
            "config": "preferred_currency",
            "value": preferred_currency.acronym,
        },
    ]

    print(tabulate(data, headers="keys"))


@config.command(name="set-currency")
@click.option("--currency-id")
@click.option("--auth-token")
def set_currency(currency_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    preferred_currency = api.get_preferred_currency(headers=headers)
    currencies = api.get_currencies(headers=headers)

    currency_id = (
        currency_id
        or currency_question(currencies, default=preferred_currency).execute()
    )

    user_settings = api.set_preferred_currency(
        data={"currency_id": currency_id}, headers=headers
    )

    print(user_settings.id)
