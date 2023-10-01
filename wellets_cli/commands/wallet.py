import click
from InquirerPy import inquirer
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.config import settings
from wellets_cli.model import Wallet
from wellets_cli.question import (
    confirm_question,
    currency_question,
    date_range_question,
    interval_question,
    wallet_question,
    warning_message,
)
from wellets_cli.util import change_value, get_currency_by_id, make_headers, pp
from wellets_cli.validator import AndValidator, EmptyInputValidator, NumberValidator


@click.group()
def wallet():
    """
    Manage money accounts (aka wallet).
    """
    pass


@wallet.command(name="list")
@click.option("--auth-token")
def list_wallets(auth_token):
    """
    List all wallets.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = api.get_currencies(headers=headers)
    wallets = api.get_wallets(headers=headers)
    base_currency = api.get_preferred_currency(headers=headers)

    def get_row_value(wallet: Wallet):
        currency = get_currency_by_id(currencies, wallet.currency_id)
        countervalue = change_value(
            currency.dollar_rate, base_currency.dollar_rate, wallet.balance
        )
        return {
            "id": wallet.id,
            "alias": wallet.alias,
            "balance": f"{currency.acronym} {pp(wallet.balance, decimals=8, fixed=False)}",
            "countervalue": f"{base_currency.acronym} {pp(countervalue, decimals=2, fixed=False)}",
            "updated_at": wallet.updated_at.strftime(settings.app.date_format),
        }

    data = list(map(get_row_value, wallets))

    print(tabulate(data, headers="keys"))


@wallet.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--currency-id")
def create_wallet(auth_token, alias, currency_id):
    """
    Create a new wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = api.get_currencies(headers=headers)

    alias = alias or inquirer.text("Alias").execute()

    currency_id = currency_id or currency_question(currencies).execute()

    data = {
        "alias": alias,
        "currency_id": currency_id,
    }

    wallet = api.create_wallet(data, headers=headers)

    print(wallet.id)


@wallet.command(name="edit")
@click.option("--auth-token")
@click.option("--wallet_id")
@click.option("--alias")
@click.option("--balance")
@click.option("-y", "--yes", is_flag=True, default=False)
def edit_wallet(auth_token, wallet_id, alias, balance, yes):
    """
    Edit a wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)

    wallet_id: str = wallet_id or wallet_question(wallets).execute()

    wallet = api.get_wallet(wallet_id, headers=headers)

    alias = (
        alias
        or inquirer.text(
            "Alias", default=wallet.alias, validate=EmptyInputValidator()
        ).execute()
    )
    balance = (
        balance
        or inquirer.number(
            "Balance",
            default=wallet.balance,
            long_instruction="Warning: changing the wallet balance may result in inconsistent data",
            float_allowed=True,
            validate=AndValidator(
                [EmptyInputValidator(), NumberValidator(float_allowed=True)]
            ),
        ).execute()
    )

    if not yes and not confirm_question().execute():
        return

    data = {
        "alias": alias,
        "balance": balance,
    }

    wallet = api.update_wallet(wallet_id, data, headers=headers)

    print(wallet.id)


@wallet.command(name="delete")
@click.option("--auth-token")
@click.option("--wallet-id")
@click.option("-y", "--yes", is_flag=True, default=False)
def delete_wallet(auth_token, wallet_id, yes):
    """
    Delete a wallet.

    WARNING: This action is irreversible and will delete all transactions
    associated with the wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    wallet_id: str = wallet_id or wallet_question(wallets).execute()

    click.echo(
        warning_message(
            "This action is irreversible and will delete all transactions associated "
            "with the wallet."
        )
    )

    if not yes and not confirm_question(default=False).execute():
        return

    wallet = api.delete_wallet(
        wallet_id=wallet_id,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    print(wallet.id)


@wallet.command(name="balance")
@click.option("--wallet-id")
@click.option("--auth-token")
def show_wallet_balance(wallet_id, auth_token):
    """
    Show the balance of a wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    wallet_id: str = wallet_id or wallet_question(wallets).execute()

    result = api.get_wallet_balance(wallet_id, headers=headers)

    print(f"{result.balance} {result.currency.acronym}")


@wallet.command(name="total-balance")
@click.option("--auth-token")
def show_wallets_total_balance(auth_token):
    """
    Show the sum of all wallets' balance.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    result = api.get_wallets_total_balance(headers=headers)

    print(f"{result.balance} {result.currency.acronym}")


@wallet.command(name="history")
@click.option("--wallet-id")
@click.option("--interval", type=click.Choice(["1d", "1w"], case_sensitive=True))
@click.option("--start-date", type=click.DateTime())
@click.option("--end-date", type=click.DateTime())
@click.option("--path", type=click.Path())
@click.option("--auth-token")
def show_wallet_history(wallet_id, interval, start_date, end_date, path, auth_token):
    """
    Show a chart with the wallet balance history.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)

    wallet_id = wallet_id or wallet_question(wallets).execute()
    interval = interval or interval_question().execute()
    start_date, end_date = (start_date and end_date) or date_range_question().execute()

    params = {
        "wallet_id": wallet_id,
        "start": start_date,
        "end": end_date,
        "interval": interval,
    }

    history = api.get_wallet_history(params=params, headers=headers)

    import matplotlib.pyplot as plt
    import numpy as np

    xs = np.array([x.timestamp for x in history])
    ys = np.array([x.balance for x in history])

    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    ax.plot(xs, ys)

    if path:
        plt.savefig(path)
        print("Saved to", path)
    else:
        plt.show()
