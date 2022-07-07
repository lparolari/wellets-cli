import click
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Transaction
from wellets_cli.question import (
    confirm_question,
    currency_question,
    dollar_rate_question,
    wallet_question,
)
from wellets_cli.util import (
    change_from,
    change_value,
    get_by_id,
    get_currency_by_acronym,
    get_currency_by_id,
    make_headers,
    pp,
)


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
            "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": transaction.updated_at.strftime("%Y-%m-%d %H:%M"),
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
    wallet = get_by_id(wallets, wallet_id)
    wallet_currency = get_by_id(currencies, wallet.currency_id)

    value = (
        value
        or inquirer.number(
            message=f"Amount ({wallet_currency.acronym})",
            float_allowed=True,
            validate=EmptyInputValidator(),
        ).execute()
    )

    if not dollar_rate:
        usd_currency = get_currency_by_acronym(
            currencies, acronym="USD", safe=True
        )

        currency_id = currency_question(
            currencies=currencies,
            message="Change rate",
            default=usd_currency,
            mandatory=False,
        ).execute()
        currency = currency_id and get_by_id(currencies, currency_id)

        change_val = (
            currency
            and inquirer.number(
                message=f"Change value (1 {wallet_currency.acronym} equals ? {currency.acronym})",
                float_allowed=True,
                min_allowed=0,
                default=change_value(
                    wallet_currency.dollar_rate, currency.dollar_rate, 1
                ),
                filter=lambda v: (1 / float(v)) * currency.dollar_rate,
                transformer=lambda v: f"{v} {currency.acronym} ≈ {change_value(1 / float(v), 1 / currency.dollar_rate, 1)} USD",
                validate=EmptyInputValidator(),
            ).execute()
        )

    dollar_rate = dollar_rate or change_val or dollar_rate_question().execute()

    description = (
        description
        or inquirer.text(
            message="Description",
            validate=EmptyInputValidator(),
        ).execute()
    )

    if not yes and not confirm_question().execute():
        return

    data = {
        "wallet_id": wallet_id,
        "value": value,
        "dollar_rate": change_from(currency.dollar_rate, dollar_rate),
        "description": description,
    }

    transaction = api.create_transaction(data, headers=headers)

    print(transaction.id)
