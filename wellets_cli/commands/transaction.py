import click
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Transaction
from wellets_cli.question import (
    confirm_question,
    dollar_rate_question,
    wallet_question,
)
from wellets_cli.util import change_value, make_headers, pp


@click.group()
def transaction():
    pass


@transaction.command(name="list")
@click.option("-id", "--wallet-id", type=click.UUID)
@click.option("-d", "--description", is_flag=True)
@click.option("--auth-token")
def list_transactions(wallet_id, description, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallet_id = (
        wallet_id
        or wallet_question(api.get_wallets(headers=headers)).execute()
    )

    transactions = api.get_transactions(
        {"wallet_id": wallet_id, "limit": 25, "page": 1}, headers=headers
    )
    preferred_currency = api.get_preferred_currency(headers=headers)

    def get_row_value(transaction: Transaction):
        countervalue = change_value(
            transaction.wallet.currency.dollar_rate,
            preferred_currency.dollar_rate,
            transaction.value,
        )
        buy_price = change_value(
            transaction.dollar_rate, preferred_currency.dollar_rate, 1
        )

        return {
            "id": transaction.id,
            "amount": f"{transaction.wallet.currency.acronym} {pp(transaction.value)}",
            "countevalue": f"{preferred_currency.acronym} {pp(countervalue)}",
            "buy_price": f"{preferred_currency.acronym} {pp(buy_price)}",
            **(
                {"description": transaction.description} if description else {}
            ),
        }

    data = list(map(get_row_value, transactions))

    print(tabulate(data, headers="keys"))


@transaction.command(name="create")
@click.option("--wallet-id", type=click.UUID)
@click.option("--value", type=float)
@click.option("--dollar-rate", type=float)
@click.option("--description", type=str)
@click.option("-y", "--yes", is_flag=True, type=bool)
@click.option("--auth-token")
def create_transaction(
    wallet_id, value, dollar_rate, description, yes, auth_token
):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    currencies = api.get_currencies(headers=headers)

    wallet_id = (
        wallet_id
        or wallet_question(
            wallets=wallets,
            message="Wallet",
        ).execute()
    )
    value = (
        value
        or inquirer.number(
            message="Value",
            float_allowed=True,
            validate=EmptyInputValidator(),
        ).execute()
    )
    dollar_rate = (
        dollar_rate or dollar_rate_question(currencies=currencies).execute()
    )
    description = (
        description
        or inquirer.text(
            message="Description",
        ).execute()
    )

    data = {
        "wallet_id": wallet_id,
        "value": value,
        "dollar_rate": dollar_rate,
        "description": description,
    }

    if not yes and not confirm_question().execute():
        return

    print("TODO")
