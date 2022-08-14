import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.config import Config
from wellets_cli.question import currency_question
from wellets_cli.util import make_headers

CONFIG_API_URL = "api.url"
CONFIG_API_USERNAME = "api.username"
CONFIG_API_PASSWORD = "api.password"
CONFIG_USER_PREFERRED_CURRENCY = "user-settings.preferred-currency"
SETTABLE_CONFIGS = [CONFIG_USER_PREFERRED_CURRENCY]


@click.group()
def config():
    pass


@config.command(name="show")
@click.option("--auth-token")
def show_config(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    preferred_currency = api.get_preferred_currency(headers=headers)

    data = [
        {"config": CONFIG_API_URL, "value": Config.api_url},
        {"config": CONFIG_API_USERNAME, "value": Config.api_username},
        {"config": CONFIG_API_PASSWORD, "value": "<sensitive>"},
        {
            "config": CONFIG_USER_PREFERRED_CURRENCY,
            "value": preferred_currency.acronym,
        },
    ]

    print(tabulate(data, headers="keys"))


@config.command(name="set")
@click.argument("config")
@click.option("--auth-token")
def set_config(config, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    if CONFIG_USER_PREFERRED_CURRENCY in config:
        preferred_currency = api.get_preferred_currency(headers=headers)
        currencies = api.get_currencies(headers=headers)

        currency_id = currency_question(
            currencies, default=preferred_currency
        ).execute()

        user_settings = api.set_preferred_currency(
            data={"currency_id": currency_id}, headers=headers
        )

    print(user_settings.id)
