import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Asset, AssetAllocation, AssetEntry
from wellets_cli.question import asset_question
from wellets_cli.util import (
    change_val,
    change_value,
    get_by_id,
    make_headers,
    pp,
)


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


@asset.command(name="exposition")
@click.option("--asset-id")
@click.option("--auth-token")
def show_asset_exposition(asset_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    currency = api.get_preferred_currency(headers=headers)

    asset_id = asset_id or asset_question(assets=assets).execute()

    result = api.get_asset_average_load_price(
        params={"asset_id": asset_id},
        headers=headers,
    )

    print(f"{currency.acronym} {pp(result.average_load_price)}")


@asset.command(name="balance")
@click.option("--asset-id")
@click.option("--auth-token")
def show_asset_balance(asset_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    currency = api.get_preferred_currency(headers=headers)

    asset_id = asset_id or asset_question(assets=assets).execute()

    result = api.get_asset_balance(
        params={"asset_id": asset_id},
        headers=headers,
    )

    print(f"{currency.acronym} {pp(result.balance)}")


@asset.command(name="allocation")
@click.option("--auth-token")
def show_asset_allocations(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currency = api.get_preferred_currency(headers=headers)
    allocations = api.get_asset_allocations(headers=headers)

    def get_row_value(allocation: AssetAllocation):
        return {
            "id": f"{allocation.asset.id}",
            "asset": f"{allocation.asset.currency.acronym}",
            "balance": f"{currency.acronym} {pp(allocation.balance)}",
            "allocation": f"{pp(allocation.allocation, percent=True, decimals=0)}",
        }

    data = [get_row_value(allocation) for allocation in allocations]

    print(tabulate(data, headers="keys"))


@asset.command(name="total-balance")
@click.option("--auth-token")
def show_total_asset_balance(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currency = api.get_preferred_currency(headers=headers)
    result = api.get_total_asset_balance(headers=headers)

    print(f"{currency.acronym} {pp(result.balance)}")


@asset.command(name="entries")
@click.option("--asset-id")
@click.option("--auth-token")
def show_asset_entries(asset_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    currency = api.get_preferred_currency(headers=headers)

    asset_id = asset_id or asset_question(assets=assets).execute()

    asset: Asset = get_by_id(assets, asset_id)
    entries = asset.entries

    def get_row_value(entry: AssetEntry):
        equivalent = change_value(
            asset.currency.dollar_rate,
            currency.dollar_rate,
            entry.value,
        )
        buy_price = change_value(entry.dollar_rate, currency.dollar_rate, 1)
        buy_equivalent = change_value(
            entry.dollar_rate,
            currency.dollar_rate,
            entry.value,
        )
        gain_wrt_buy_price = (equivalent - buy_equivalent) / buy_equivalent

        return {
            "id": entry.id,
            "amount": f"{asset.currency.acronym} {pp(entry.value, decimals=8, fixed=False)}",
            "buy_price": f"{currency.acronym} {pp(buy_price)}",
            "buy_amount": f"{currency.acronym} {pp(buy_equivalent)}",
            "equivalent": f"{currency.acronym} {pp(equivalent)} ({pp(gain_wrt_buy_price, percent=True, decimals=0)})",
            "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M"),
        }

    data = [get_row_value(entry) for entry in entries]

    print(tabulate(data, headers="keys"))
