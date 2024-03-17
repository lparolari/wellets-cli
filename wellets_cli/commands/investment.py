from typing import Optional

import click
from InquirerPy import inquirer
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.commands.transaction import create_transaction
from wellets_cli.model import Investment
from wellets_cli.question import (
    accumulation_question,
    asset_question,
    date_question,
    duration_question,
)
from wellets_cli.util import format_duration, get_by_id, make_headers, pp
from wellets_cli.validator import (
    AndValidator,
    EmptyInputValidator,
    GreaterThanValidator,
    NumberValidator,
)


@click.group(
    deprecated=True
)  # actually, this should be in a separate feature branch (see feature/investments)
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

    investments = api.get_investments(headers=headers)

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
