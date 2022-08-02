import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Asset
from wellets_cli.util import change_val, make_headers, pp


@click.group()
def asset():
    pass


@asset.command(name="list")
@click.option("--auth-token")
def list_assets(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    currency = api.get_preferred_currency(headers=headers)

    def get_row_value(asset: Asset):
        equivalent = change_val(asset.currency, currency, asset.balance)
        return {
            "id": asset.id,
            "balance": f"{asset.currency.acronym} {pp(asset.balance, decimals=8, fixed=False)}",
            "equivalent": f"{currency.acronym} {pp(equivalent, decimals=2, fixed=False)}",
            "entries": len(asset.entries),
        }

    data = [get_row_value(asset) for asset in assets]

    print(tabulate(data, headers="keys"))
