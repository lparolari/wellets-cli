import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Asset, AssetAllocation, AssetEntry
from wellets_cli.question import asset_question, interval_question, date_range_question
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
            f"balance\n({currency.acronym})": pp(allocation.balance, 0),
            "allocation\n(%)": f"{pp(allocation.allocation, 1, percent=True)}",
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
        gain_wrt_buy_price = (equivalent - buy_equivalent) / (buy_equivalent or 1)

        return {
            "id": entry.id,
            f"amount\n({asset.currency.acronym})": pp(entry.value, 8, fixed=False),
            f"buy_price\n({currency.acronym})": pp(buy_price, 0),
            f"buy_amount\n({currency.acronym})": pp(buy_equivalent),
            f"equivalent\n({currency.acronym})": pp(equivalent),
            f"profit\n(%)": pp(gain_wrt_buy_price, percent=True, decimals=0),
            "created_at": entry.created_at.strftime("%b %d, %Y"),
        }

    data = [get_row_value(entry) for entry in entries]

    print(tabulate(data, headers="keys"))


@asset.command(name="history")
@click.option("--asset-id")
@click.option("--interval", type=click.Choice(["1d", "1w"], case_sensitive=True))
@click.option("--start-date", type=click.DateTime())
@click.option("--end-date", type=click.DateTime())
@click.option("--path", type=click.Path())
@click.option("--auth-token")
def show_asset_history(asset_id, interval, start_date, end_date, path, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)

    asset_id = asset_id or asset_question(assets).execute()
    interval = interval or interval_question(default="1d").execute()
    start_date, end_date = (start_date and end_date) or date_range_question().execute()

    params = {
        "asset_id": asset_id,
        "start": start_date,
        "end": end_date,
        "interval": interval,
    }

    history = api.get_asset_history(params=params, headers=headers)
    asset = get_by_id(assets, asset_id)

    import matplotlib.pyplot as plt
    import numpy as np

    xs = np.array([x.timestamp for x in history])
    ys = np.array([x.balance for x in history])

    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    ax.plot(xs, ys, "-o", label=asset.currency.acronym)
    ax.legend()
    ax.set_xlabel("Date")
    ax.set_ylabel("Balance")

    for i, balance in enumerate(ys):
        ax.annotate(
            f"{balance:.2f}",
            (xs[i], balance),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
        )

    if path:
        plt.savefig(path)
        print("Saved to", path)
    else:
        plt.show()
