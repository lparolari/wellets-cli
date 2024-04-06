from datetime import datetime

import click
from InquirerPy import inquirer
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.config import settings
from wellets_cli.model import Wallet
from wellets_cli.question import (
    change_value_question,
    confirm_question,
    currency_question,
    date_question,
    date_range_question,
    dollar_rate_question,
    interval_question,
    wallet_question,
    warning_message,
)
from wellets_cli.util import (
    change_value,
    get_by_id,
    get_currency_by_acronym,
    get_currency_by_id,
    make_headers,
    pp,
)
from wellets_cli.validator import (
    AndValidator,
    EmptyInputValidator,
    GreaterThanOrEqualValidator,
    NumberValidator,
)


@click.group()
def wallet():
    """
    Manage money accounts (aka wallet).
    """
    pass


@wallet.command(name="list")
@click.option("--auth-token")
@click.option("-c", "--compact", is_flag=True, default=False)
def list_wallets(auth_token, compact):
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
            "updated_at": wallet.updated_at.strftime(settings.date_format),
            **({} if compact else {"desc": wallet.description}),
        }

    data = list(map(get_row_value, wallets))

    print(tabulate(data, headers="keys"))


@wallet.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--description")
@click.option("--currency-id")
def create_wallet(auth_token, alias, description, currency_id):
    """
    Create a new wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = api.get_currencies(headers=headers)

    alias = alias or inquirer.text("Alias", validate=EmptyInputValidator()).execute()

    description = (
        description
        or inquirer.text("Description", filter=lambda x: x or None).execute()
    )

    currency_id = currency_id or currency_question(currencies).execute()

    data = {
        "alias": alias,
        "description": description,
        "currency_id": currency_id,
    }

    wallet = api.create_wallet(data, headers=headers)

    print(wallet.id)


@wallet.command(name="edit")
@click.option("--auth-token")
@click.option("--wallet_id")
@click.option("--alias")
@click.option("--description")
@click.option("--balance")
@click.option("-y", "--yes", is_flag=True, default=False)
def edit_wallet(auth_token, wallet_id, alias, description, balance, yes):
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

    description = (
        description
        or inquirer.text(
            "Description",
            default=wallet.description or "",
            filter=lambda x: x or None,
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
        "description": description,
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


@wallet.command(name="show")
@click.option("--auth-token")
@click.option("--wallet_id")
def show_wallet(auth_token, wallet_id):
    """
    Show a wallet.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    wallet_id: str = wallet_id or wallet_question(wallets).execute()

    wallet = api.get_wallet(wallet_id, headers=headers)

    data = [
        {"key": "id", "value": wallet.id},
        {"key": "alias", "value": wallet.alias},
        {"key": "balance", "value": wallet.balance},
        {"key": "currency", "value": wallet.currency.acronym},
        {"key": "desc", "value": wallet.description or "-"},
        {
            "key": "created_at",
            "value": wallet.created_at.strftime(settings.datetime_format),
        },
        {
            "key": "updated_at",
            "value": wallet.updated_at.strftime(settings.datetime_format),
        },
        {
            "key": "portfolios",
            "value": f"{len(wallet.portfolios)} attached",
        },
    ]

    print(tabulate(data, headers="keys"))


@wallet.command(name="balance:get")
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


@wallet.command(name="balance:set")
@click.option("--wallet-id")
@click.option("--new-balance", type=float)
@click.option("--dollar-rate", type=float)
@click.option("--change-currency-id", type=click.UUID)
@click.option("--change-val", type=float)
@click.option("--description", type=str)
@click.option("--created-at", type=click.DateTime(formats=["%Y-%m-%d %H:%M"]))
@click.option("-y", "--yes", is_flag=True, default=False)
@click.option("--auth-token")
def set_wallet_balance(
    wallet_id,
    new_balance,
    dollar_rate,
    change_currency_id,
    change_val,
    description,
    created_at,
    yes,
    auth_token,
):
    """
    Set the balance of a wallet.

    A new transaction is created with the value of the difference between the
    new balance and the wallet balance before the change.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    currencies = api.get_currencies(headers=headers)
    preferred_currency = api.get_preferred_currency(headers=headers)

    wallet_id: str = wallet_id or wallet_question(wallets).execute()
    wallet: Wallet = get_by_id(wallets, wallet_id)
    wallet_currency = get_by_id(currencies, wallet.currency_id)

    prev_balance = wallet.balance

    new_balance = (
        new_balance
        or inquirer.number(
            message=f"New balance ({wallet_currency.acronym})",
            default=prev_balance,
            float_allowed=True,
            validate=AndValidator(
                [EmptyInputValidator(), GreaterThanOrEqualValidator(0)]
            ),
            filter=lambda x: float(x),
        ).execute()
    )

    value = new_balance - prev_balance

    if not dollar_rate:
        usd_currency = get_currency_by_acronym(currencies, acronym="USD", safe=True)

        currency_id = (
            change_currency_id
            or currency_question(
                currencies=currencies,
                message="Change rate",
                default=usd_currency,
                mandatory=False,
            ).execute()
        )
        currency = currency_id and get_by_id(currencies, currency_id)

        change_val = change_val or (
            currency
            and change_value_question(
                source_currency=wallet_currency,
                target_currency=currency,
            ).execute()
        )

    dollar_rate = dollar_rate or change_val or dollar_rate_question().execute()

    description = (
        description
        or inquirer.text(
            message="Description",
            default="Balance change",
            validate=EmptyInputValidator(),
        ).execute()
    )

    created_at = (
        created_at
        or date_question(
            message="Created at (yyyy-MM-dd HH:mm)",
            default=datetime.now(),
            date_fmt="%Y-%m-%d %H:%M",
        ).execute()
    )

    if (
        not yes
        and not confirm_question(
            message=f"Confirm buy/sell of {wallet_currency.acronym} {pp(value)} ~ {preferred_currency.acronym} {pp(change_value(dollar_rate, preferred_currency.dollar_rate, value))} "
            f"({wallet_currency.acronym} {pp(prev_balance)} ~ {preferred_currency.acronym} {pp(change_value(dollar_rate, preferred_currency.dollar_rate, prev_balance))} -> "
            f"{wallet_currency.acronym} {pp(new_balance)} ~ {preferred_currency.acronym} {pp(change_value(dollar_rate, preferred_currency.dollar_rate, new_balance))})"
        ).execute()
    ):
        return

    data = {
        "wallet_id": wallet_id,
        "value": value,
        "dollar_rate": dollar_rate,
        "description": description,
        "created_at": created_at,
    }

    api.create_transaction(data, headers=headers)

    print(wallet_id)


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
