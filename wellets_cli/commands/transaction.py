import json

import click
from wellets_cli.auth import get_auth_token

import wellets_cli.api as api
from wellets_cli.model import Transaction
from wellets_cli.question import wallet_question
from tabulate import tabulate

from wellets_cli.util import change_from, change_value, make_headers
@click.group()
def transaction():
    pass


@transaction.command(name="list")
@click.option("-id", "--wallet-id", type=click.UUID)
@click.option("--auth-token")
def list_transactions(wallet_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallet_id = wallet_id or wallet_question(api.get_wallets(headers=headers)).execute()
    
    preferred_currency = api.get_preferred_currency(headers=headers)
    transactions = api.get_transactions({"wallet_id": wallet_id, "limit": 25, "page": 1}, headers=headers)  

    def get_row_value(transaction: Transaction):
        return {
            "id": transaction.id,
            "amount": transaction.value,
            "countevalue": change_value(transaction.dollar_rate, preferred_currency.dollar_rate, transaction.value),
            "buy_price": change_value(transaction.dollar_rate, preferred_currency.dollar_rate, 1),
            "wallet": transaction.wallet.alias
        }

    data = list(map(get_row_value, transactions))

    print(tabulate(data, headers="keys"))
