from datetime import datetime

import click
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Transaction
from wellets_cli.question import (
    accumulation_question,
    change_value_question,
    confirm_question,
    currency_question,
    dollar_rate_question,
    transaction_question,
    wallet_question,
)
from wellets_cli.util import (
    change_value,
    get_by_id,
    get_currency_by_acronym,
    make_headers,
    pp,
)
from wellets_cli.validator import (
    AndValidator,
    DateValidator,
    GreaterThanOrEqualValidator,
)


@click.group()
def transaction():
    pass


@transaction.command(name="list")
@click.option("-id", "--wallet-id", type=click.UUID)
@click.option("--auth-token")
def list_transactions(wallet_id, auth_token):
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
        equivalent = change_value(
            transaction.wallet.currency.dollar_rate,  # type: ignore
            preferred_currency.dollar_rate,
            transaction.value,
        )

        return {
            "id": transaction.id,
            "amount": f"{transaction.wallet.currency.acronym} {pp(transaction.value, decimals=8, fixed=False)}",  # type: ignore
            "equivalent": f"{preferred_currency.acronym} {pp(equivalent)}",
            "description": transaction.description,
            "created_at": transaction.created_at.strftime("%Y-%m-%d %H:%M"),
        }

    data = list(map(get_row_value, transactions))

    print(tabulate(data, headers="keys"))


@transaction.command(name="create")
@click.option("--wallet-id", type=click.UUID)
@click.option("--value", type=float)
@click.option("--dollar-rate", type=float)
@click.option("--change-currency-id", type=click.UUID)
@click.option("--change-val", type=float)
@click.option("--description", type=str)
@click.option("--accumulation-id", type=str)
@click.option("--created-at", type=click.DateTime(formats=["%Y-%m-%d %H:%M"]))
@click.option("-y", "--yes", is_flag=True, type=bool)
@click.option("--auth-token")
def create_transaction(
    wallet_id,
    value,
    dollar_rate,
    change_currency_id,
    change_val,
    description,
    created_at,
    accumulation_id,
    yes,
    auth_token,
):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    currencies = api.get_currencies(headers=headers)
    preferred_currency = api.get_preferred_currency(headers=headers)

    wallet_id = (
        wallet_id
        or wallet_question(
            wallets=wallets,
            message="Wallet",
        ).execute()
    )
    wallet = get_by_id(wallets, wallet_id)
    wallet_currency = get_by_id(currencies, wallet.currency_id)

    accumulations = api.get_accumulations(params={}, headers=headers)

    accumulation_id = accumulation_id or (
        accumulation_question(accumulations, allow_none=True).execute()
        if len(accumulations) > 0
        else None
    )

    transaction_type = inquirer.select(
        message="Transaction type",
        choices=["Income", "Outcome"],
        default="Income",
    ).execute()

    value = (
        value
        or inquirer.number(
            message=f"{transaction_type} amount ({wallet_currency.acronym})",
            float_allowed=True,
            validate=AndValidator(
                [EmptyInputValidator(), GreaterThanOrEqualValidator(0)]
            ),
            filter=lambda x: float(x)
            * (1 if transaction_type == "Income" else -1),
        ).execute()
    )

    if not dollar_rate:
        usd_currency = get_currency_by_acronym(
            currencies, acronym="USD", safe=True
        )

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
            default="Buy",
            validate=EmptyInputValidator(),
        ).execute()
    )

    created_at = (
        created_at
        or inquirer.text(
            message="Created at (yyyy-MM-dd HH:mm)",
            default=datetime.now().strftime("%Y-%m-%d %H:%M"),
            validate=AndValidator([EmptyInputValidator(), DateValidator()]),
        ).execute()
    )

    if (
        not yes
        and not confirm_question(
            message=f"Confirm buy/sell of {preferred_currency.acronym} {pp(change_value(dollar_rate, preferred_currency.dollar_rate, value))}"
        ).execute()
    ):
        return

    data = {
        "wallet_id": wallet_id,
        "accumulation_id": accumulation_id,
        "value": value,
        "dollar_rate": dollar_rate,
        "description": description,
        "created_at": created_at,
    }

    transaction = api.create_transaction(data, headers=headers)

    print(transaction.id)


@transaction.command(name="revert")
@click.option("--wallet-id", type=click.UUID)
@click.option("--transaction-id", type=click.UUID)
@click.option("--auth-token")
def revert_transaction(wallet_id, transaction_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)
    wallet_id = wallet_id or wallet_question(wallets).execute()

    transactions = api.get_transactions(
        {"wallet_id": wallet_id}, headers=headers
    )
    transaction_id = (
        transaction_id or transaction_question(transactions).execute()
    )

    reverted = api.revert_transaction(transaction_id, headers=headers)

    print(reverted.id)
