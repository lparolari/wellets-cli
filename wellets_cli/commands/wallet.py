import click
from InquirerPy import inquirer
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Wallet
from wellets_cli.prompt import prompt_wallet
from wellets_cli.question import currency_question
from wellets_cli.util import change_value, get_currency_by_id, make_headers, pp


@click.group()
def wallet():
    pass


@wallet.command(name="list")
@click.option("--auth-token")
def list_wallets(auth_token):
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
            "created_at": wallet.created_at.strftime("%Y-%m-%d"),
        }

    data = list(map(get_row_value, wallets))

    print(tabulate(data, headers="keys"))


@wallet.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--currency-id")
def create_wallet(auth_token, alias, currency_id):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    currencies = api.get_currencies(headers=headers)

    alias = alias or inquirer.text("Alias").execute()

    currency_id = currency_id or currency_question(currencies).execute()

    data = {
        "alias": alias,
        "currency_id": currency_id,
        "balance": 0,
    }

    wallet = api.create_wallet(data, headers=headers)

    print(wallet.id)


@wallet.command(name="delete")
@click.option("--auth-token")
@click.option("--wallet-id")
def delete_wallet(auth_token, wallet_id):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)
    requires_interaction = wallet_id is None

    wallets = api.get_wallets(headers=headers)

    if requires_interaction:
        wallet_id = prompt_wallet(wallets)

    wallet = api.delete_wallet(
        wallet_id=wallet_id,
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    print(wallet.id)


@wallet.command(name="balance")
@click.option("--wallet-id")
@click.option("--auth-token")
def show_wallet_balance(wallet_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)
    requires_interaction = wallet_id is None

    if requires_interaction:
        wallet_id = prompt_wallet(api.get_wallets(headers=headers))

    result = api.get_wallet_balance(wallet_id, headers=headers)

    print(f"{result.balance} {result.currency.acronym}")


@wallet.command(name="total-balance")
@click.option("--auth-token")
def show_wallets_total_balance(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    result = api.get_wallets_total_balance(headers=headers)

    print(f"{result.balance} {result.currency.acronym}")
