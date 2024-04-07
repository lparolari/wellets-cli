from datetime import timedelta

import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.chart import (
    mk_fig,
    plot_allocation,
    plot_balance,
    plot_ema,
    plot_exposition,
    plot_position,
    plot_price,
    show_chart,
    xdate_fmt,
)
from wellets_cli.config import settings
from wellets_cli.model import Asset, AssetAllocation, AssetEntry
from wellets_cli.question import asset_question, date_range_question, interval_question
from wellets_cli.util import change_val, change_value, get_by_id, make_headers, pp


@click.group()
def asset():
    """
    Manage financial assets.
    """
    pass


@asset.command(name="list")
@click.option("--auth-token")
def list_assets(auth_token):
    """
    List all assets.
    """
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
    """
    Show the average cost basis of an asset.
    """
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
    """
    Show the total balance of an asset.
    """
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
    """
    Show a chart of the asset allocations.
    """
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

    fig = mk_fig()
    fig = plot_allocation(fig, allocations)
    fig = show_chart(fig)


@asset.command(name="total-balance")
@click.option("--auth-token")
def show_total_asset_balance(auth_token):
    """
    Show the total balance of all assets.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currency = api.get_preferred_currency(headers=headers)
    result = api.get_total_asset_balance(headers=headers)

    print(f"{currency.acronym} {pp(result.balance)}")


@asset.command(name="entries")
@click.option("--asset-id")
@click.option("--auth-token")
def show_asset_entries(asset_id, auth_token):
    """
    List all income/outcome transactions of an asset.
    """
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
    """
    Show the balance history of an asset.
    """
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

    data = [
        {
            "timestamp": h.timestamp.strftime(settings.date_format),
            f"balance\n({asset.currency.acronym})": pp(h.balance, 8, fixed=False),
        }
        for h in history
    ]

    print(tabulate(data, headers="keys"))

    fig = mk_fig()
    fig = plot_balance(fig, history, label=asset.currency.acronym)
    fig = show_chart(fig, path)


@asset.command(name="visualize")
@click.option("-id", "--asset-id")
@click.option("--auth-token")
def visualize(asset_id, auth_token):
    """
    Visualize transactions cost basis on the asset price chart.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    base_currency = api.get_preferred_currency(headers=headers)

    asset_id = asset_id or asset_question(assets=assets).execute()

    asset: Asset = get_by_id(assets, asset_id)
    currency = asset.currency
    entries = asset.entries
    exposition = api.get_asset_average_load_price(
        params={"asset_id": asset_id},
        headers=headers,
    )

    date_min = min([e.created_at for e in entries])
    date_max = max([e.created_at for e in entries]) + timedelta(days=1)

    history = api.get_currency_history(
        {
            "currency_id": asset.currency_id,
            "interval": "1d",
            "start_time": date_min.strftime("%Y-%m-%d"),
            "end_time": date_max.strftime("%Y-%m-%d"),
        },
        headers=headers,
    )

    price_date = [h.open_time for h in history]
    price = [
        change_value(1 / h.close_price, base_currency.dollar_rate, 1) for h in history
    ]

    position_date = [e.created_at for e in entries]
    position = [
        change_value(e.dollar_rate, base_currency.dollar_rate, 1) for e in entries
    ]
    size_max = max([abs(e.value) for e in entries])
    size = [abs(e.value) / size_max for e in entries]
    kind = ["buy" if e.value >= 0 else "sell" for e in entries]

    fig = mk_fig()
    fig = plot_price(
        fig,
        price_date,
        price,
        label=currency.acronym,
        ylabel=f"Price ({base_currency.acronym})",
    )
    fig = plot_exposition(fig, exposition.average_load_price)
    fig = plot_position(fig, position_date, position, size, kind)
    fig = plot_ema(fig, price_date, price, window=30, color="orange")
    fig = plot_ema(fig, price_date, price, window=100, color="orchid")
    fig = xdate_fmt(fig)
    ax = fig.gca()
    ax.legend()
    show_chart(fig)


@asset.command(name="capital-gain")
@click.option("--auth-token")
@click.option("--asset-id")
def show_capital_gain(auth_token, asset_id):
    """
    Show the capital gain of an asset according to the average cost basis.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    assets = api.get_assets(headers=headers)
    currency = api.get_preferred_currency(headers=headers)

    asset_id = asset_id or asset_question(assets=assets).execute()

    capital_gain = api.get_capital_gain(params={"asset_id": asset_id}, headers=headers)

    data = [
        {
            "key": "current_price",
            "value": f"{currency.acronym} {pp(capital_gain.current_price)}",
        },
        {
            "key": "basis_price",
            "value": f"{currency.acronym} {pp(capital_gain.basis_price)}",
        },
        {
            "key": "gain_amount",
            "value": f"{currency.acronym} {pp(capital_gain.gain_amount)}",
        },
        {
            "key": "gain_percent",
            "value": f"{pp(capital_gain.gain_rate, percent=True, with_symbol=True)}",
        },
    ]

    print(tabulate(data, headers="keys"))
