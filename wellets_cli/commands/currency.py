import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Currency
from wellets_cli.util import change_value, make_headers


@click.group()
def currency():
    pass


@currency.command(name="list")
@click.option("--auth-token")
def list_currencies(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = api.get_currencies(headers=headers)

    def get_row_value(currency: Currency):
        return {
            "id": currency.id,
            "acronym": currency.acronym,
            "alias": currency.alias,
            "dollar_rate": currency.dollar_rate,
            "countervalue": change_value(currency.dollar_rate, 1, 1),
            "updated_at": currency.updated_at.strftime("%Y-%m-%d %H:%M"),
            "created_at": currency.created_at.strftime("%Y-%m-%d"),
        }

    data = list(map(get_row_value, currencies))

    print(tabulate(data, headers="keys"))
