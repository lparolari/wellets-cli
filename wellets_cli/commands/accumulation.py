import click
from InquirerPy import inquirer
from pytest import param
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.commands.transaction import create_transaction
from wellets_cli.model import Accumulation, AccumulationEntry
from wellets_cli.question import (
    accumulation_question,
    date_question,
    duration_question,
    wallet_question,
)
from wellets_cli.util import format_duration, get_by_id, make_headers, pp
from wellets_cli.validator import (
    AndValidator,
    EmptyInputValidator,
    GreaterThanValidator,
    NumberValidator,
)


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

    accumulations = api.get_accumulations(
        {"wallet_id": wallet_id}, headers=headers
    )

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

    if not accumulation:
        return

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

    if not accumulation:
        return

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
@click.option("--wallet-id")
@click.option("--alias")
@click.option("--strategy")
@click.option("--quote")
@click.option("--planned-entries")
@click.option("--every")
@click.option("--planned-start")
@click.option("--planned-end")
@click.option("--auth-token")
def create_accumulation(
    wallet_id,
    alias,
    strategy,
    quote,
    planned_entries,
    every,
    planned_start,
    planned_end,
    auth_token,
):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallets = api.get_wallets(headers=headers)

    wallet_id = wallet_id or wallet_question(wallets).execute()

    alias = (
        alias
        or inquirer.text(
            message="Alias",
            validate=EmptyInputValidator(),
        ).execute()
    )

    strategy = (
        strategy
        or inquirer.text(
            message="Strategy", validate=EmptyInputValidator()
        ).execute()
    )

    quote = (
        quote
        or inquirer.number(
            message="Quote",
            float_allowed=True,
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=True),
                    GreaterThanValidator(0),
                ]
            ),
        ).execute()
    )

    planned_entries = (
        planned_entries
        or inquirer.number(
            message="Planned entries",
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=False),
                    GreaterThanValidator(0),
                ]
            ),
        ).execute()
    )

    every = duration_question(message="Every").execute()

    planned_start = (
        planned_start
        or date_question(message="Planned start (yyyy-MM-dd HH:mm)").execute()
    )

    planned_end = (
        planned_end
        or date_question(
            message="Planned end (yyyy-MM-dd HH:mm)", default=None
        ).execute()
    )

    data = {
        "wallet_id": wallet_id,
        "alias": alias,
        "strategy": strategy,
        "quote": quote,
        "planned_entries": planned_entries,
        "every": every,
        "planned_start": planned_start,
        "planned_end": planned_end,
    }

    api.create_accumulation(data=data, headers=headers)


@accumulation.command(name="delete")
@click.option("--wallet-id")
@click.option("--accumulation-id")
@click.option("--auth-token")
def delete_accumulation(wallet_id, accumulation_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    if not accumulation_id:
        wallet = __prompt_wallet(wallet_id, headers)
        accumulation = __prompt_accumulation(
            wallet.id, accumulation_id, headers
        )

    accumulation_id = accumulation_id or accumulation.id

    accumulation = api.delete_accumulation(
        accumulation_id=accumulation_id,
        headers=headers,
    )

    print(accumulation.id)


@accumulation.command(name="create-entry")
@click.option("--wallet-id", type=click.UUID)
@click.option("--value", type=float)
@click.option("--dollar-rate", type=float)
@click.option("--change-currency-id", type=click.UUID)
@click.option("--change-val", type=float)
@click.option("--description", type=str)
@click.option("--accumulation-id", type=click.UUID)
@click.option("--created-at", type=click.DateTime(formats=["%Y-%m-%d %H:%M"]))
@click.option("-y", "--yes", is_flag=True, type=bool)
@click.option("--auth-token")
@click.pass_context
def create_entry(ctx, **kwargs):
    print(kwargs)
    wallet_id = kwargs["wallet_id"]
    accumulation_id = kwargs["accumulation_id"]
    auth_token = kwargs["auth_token"]
    description = kwargs["description"]

    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    wallet = __prompt_wallet(wallet_id, headers)
    accumulation = __prompt_accumulation(wallet.id, accumulation_id, headers)

    if not accumulation:
        return

    next_entry = api.get_next_accumulation_entry(
        accumulation.id, headers=headers
    )

    description = (
        description
        or inquirer.text(
            message="Description",
            default=f"{accumulation.alias} entry #{next_entry.entry}",
            validate=EmptyInputValidator(),
        ).execute()
    )

    params = {
        **kwargs,
        "wallet_id": wallet.id,
        "accumulation_id": accumulation.id,
        "description": description,
    }

    ctx.invoke(create_transaction, **params)


def __prompt_wallet(wallet_id, headers):
    wallets = api.get_wallets(headers=headers)

    wallet_id = wallet_id or wallet_question(wallets=wallets).execute()

    return api.get_wallet(wallet_id, headers=headers)


def __prompt_accumulation(wallet_id, accumulation_id, headers):
    accumulations = api.get_accumulations(
        {"wallet_id": wallet_id}, headers=headers
    )

    if len(accumulations) == 0:
        return None

    accumulation_id = (
        accumulation_id
        or accumulation_question(accumulations=accumulations).execute()
    )

    accumulation = get_by_id(accumulations, accumulation_id)

    return accumulation
