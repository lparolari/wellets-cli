import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Transaction
from wellets_cli.question import wallet_question
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
            **({"description": transaction.description} if description else {}),
        }

    data = list(map(get_row_value, transactions))

    print(tabulate(data, headers="keys"))
