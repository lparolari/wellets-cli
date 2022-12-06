import click
from InquirerPy import inquirer
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Investment, InvestmentEntry
from wellets_cli.question import (
    investment_entry_data_question,
    investment_question,
)
from wellets_cli.util import get_by_id, make_headers, pp
from wellets_cli.validator import EmptyInputValidator


@click.group()
def investment():
    pass


@investment.command(name="create")
@click.option("--alias")
@click.option("--auth-token")
def create_investment(alias, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    alias = (
        alias
        or inquirer.text(
            message="Alias",
            validate=EmptyInputValidator("Alias cannot be empty"),
        ).execute()
    )

    investment = api.create_investment({"alias": alias}, headers=headers)

    print(investment.id)


@investment.command(name="list")
@click.option("--auth-token")
def list_investments(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    investments = api.get_investments(params={}, headers=headers)

    def get_row(investment: Investment):
        return {
            "id": investment.id,
            "alias": investment.alias,
            "status": investment.status,
            "started_at": investment.started_at
            and investment.started_at.strftime("%Y-%m-%d"),
            "ended_at": investment.ended_at
            and investment.ended_at.strftime("%Y-%m-%d"),
        }

    data = [get_row(investment) for investment in investments]

    print(tabulate(data, headers="keys"))


@investment.command(name="start")
@click.option("-id", "--investment-id")
@click.option("--auth-token")
def start_investment(investment_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    investments = api.get_investments(
        params={"status": "created"}, headers=headers
    )
    wallets = api.get_wallets(headers=headers)
    currencies = api.get_currencies(headers=headers)

    if not len(investments):
        print("No investments to start, create one first")
        return

    investment_id = investment_id or investment_question(investments).execute()
    investment = get_by_id(investments, investment_id)

    entries = []

    while True:
        entry = investment_entry_data_question(
            wallets, currencies, investment, entry_type="input"
        ).execute()
        entries.append(entry)

        more = inquirer.confirm(
            message="Add more entries?", default=True
        ).execute()

        if not more:
            break

    ok = inquirer.confirm(
        message=f"Starting investment with {len(entries)} entries. Are you sure?",
        default=True,
    ).execute()

    if not ok:
        return

    data = {"entries": entries}

    investment = api.start_investment(
        investment_id, data=data, headers=headers
    )

    print(investment.id)


@investment.command(name="close")
@click.option("-id", "--investment-id")
@click.option("--auth-token")
def close_investment(investment_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    investments = api.get_investments(
        params={"status": "started"}, headers=headers
    )
    wallets = api.get_wallets(headers=headers)
    currencies = api.get_currencies(headers=headers)

    if not len(investments):
        print("No investments to close, start one first")
        return

    investment_id = investment_id or investment_question(investments).execute()
    investment = get_by_id(investments, investment_id)

    entries = []

    while True:
        entry = investment_entry_data_question(
            wallets, currencies, investment, entry_type="output"
        ).execute()
        entries.append(entry)

        more = inquirer.confirm(
            message="Add more entries?", default=True
        ).execute()

        if not more:
            break

    ok = inquirer.confirm(
        message=f"Closing investment with {len(entries)} entries. Are you sure?",
        default=True,
    ).execute()

    if not ok:
        return

    data = {"entries": entries}

    investment = api.close_investment(
        investment_id, data=data, headers=headers
    )

    print(investment.id)


@investment.command(name="show")
@click.option("-id", "--investment-id")
@click.option("--auth-token")
def show_investment(investment_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    investments = api.get_investments(params={}, headers=headers)

    if not len(investments):
        return
    
    investment_id = investment_id or investment_question(investments).execute()

    investment = api.get_investment(investment_id, headers=headers)

    def get_row(entry: InvestmentEntry):
        return {
            "id": entry.id,
            "type": entry.kind,
            "wallet": entry.wallet.alias,
            "amount": f"{entry.wallet.currency.acronym} {pp(entry.value, decimals=1)}",
        }
    
    data = [get_row(entry) for entry in investment.entries]

    print(tabulate(data, headers="keys"))
