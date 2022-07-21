import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Accumulation, AccumulationEntry
from wellets_cli.question import accumulation_question, wallet_question
from wellets_cli.util import format_duration, get_by_id, make_headers, pp


@click.group()
def accumulation():
    pass


@accumulation.command(name="list")
@click.option("--wallet-id")
@click.option("--auth-token")
def list_accumulations(wallet_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)

    wallet_id = wallet_id or wallet_question(wallets=wallets).execute()

    accumulations = api.get_accumulations(wallet_id, headers=headers)

    def get_accumulation_row(accumulation: Accumulation):
        return {
            "id": accumulation.id,
            "alias": accumulation.alias,
            "strategy": accumulation.strategy,
            "quote": accumulation.quote,
            "planned_entries": accumulation.planned_entries,
            "every": format_duration(accumulation.every),
            "planned_start": accumulation.planned_start.strftime("%Y-%m-%d"),
            "planned_start": accumulation.planned_end.strftime("%Y-%m-%d"),
        }

    data = [get_accumulation_row(a) for a in accumulations]

    print(tabulate(data, headers="keys"))


@accumulation.command(name="show")
@click.option("--wallet-id")
@click.option("--accumulation-id")
@click.option("--auth-token")
def show_accumulation(wallet_id, accumulation_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallet = __prompt_wallet(wallet_id, headers)
    accumulation = __prompt_accumulation(wallet.id, accumulation_id, headers)

    def get_entry_row(entry: AccumulationEntry):
        return {
            "id": entry.id,
            "amount": f"{wallet.currency.acronym} {pp(entry.value, decimals=8, fixed=False)}",
            "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M"),
            "updated_at": entry.updated_at.strftime("%Y-%m-%d %H:%M"),
            "description": entry.description,
        }

    data = [get_entry_row(e) for e in accumulation.entries]

    print(tabulate(data, headers="keys"))


@accumulation.command(name="next-entry")
@click.option("--wallet-id")
@click.option("--accumulation-id")
@click.option("--auth-token")
def show_next_entry(wallet_id, accumulation_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallet = __prompt_wallet(wallet_id, headers)
    accumulation = __prompt_accumulation(wallet.id, accumulation_id, headers)

    next_accumulation_entry = api.get_next_accumulation_entry(
        accumulation.id, headers=headers
    )

    print(
        tabulate(
            [
                {"key": "Entry", "value": next_accumulation_entry.entry},
                {"key": "Amount", "value": next_accumulation_entry.amount},
                {"key": "Current", "value": next_accumulation_entry.current},
                {"key": "Target", "value": next_accumulation_entry.target},
                {
                    "key": "Date",
                    "value": next_accumulation_entry.date.strftime("%Y-%m-%d"),
                },
            ]
        )
    )


@accumulation.command(name="create")
@click.option("--auth-token")
def create_accumulation(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    data = {
        "wallet_id": "9944e165-e393-4392-b76b-ee4f94597537",
        "alias": "Test accumulation",
        "strategy": "simple",
        "quote": 15,
        "planned_entries": 10,
        "every": {
            "days": 1
        },
        "planned_start": "2020-01-01",
        "planned_end": "2020-01-31",
    }

    api.create_accumulation(data=data, headers=headers)


def __prompt_wallet(wallet_id, headers):
    wallets = api.get_wallets(headers=headers)

    wallet_id = wallet_id or wallet_question(wallets=wallets).execute()

    return api.get_wallet(wallet_id, headers=headers)


def __prompt_accumulation(wallet_id, accumulation_id, headers):
    accumulations = api.get_accumulations(wallet_id, headers=headers)

    accumulation_id = (
        accumulation_id
        or accumulation_question(accumulations=accumulations).execute()
    )

    accumulation = get_by_id(accumulations, accumulation_id)

    return accumulation
