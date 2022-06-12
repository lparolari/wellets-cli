import click
from PyInquirer import prompt
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Portfolio, RebalanceChange
from wellets_cli.prompt import prompt_portfolio
from wellets_cli.question import (
    confirm_question,
    portfolio_question,
    q,
    wallets_question,
)
from wellets_cli.util import make_headers, pp
from wellets_cli.validator import (
    and_validator,
    each_validator,
    not_empty_validator,
    number_validator,
    percent_validator,
    uuid_validator,
    validate,
)


@click.group()
def portfolio():
    pass


@portfolio.command(name="list")
@click.option("-id", "--portfolio-id")
@click.option("-f", "--flatten", is_flag=True)
@click.option("-a", "--all", "show_all", is_flag=True)
@click.option("-i", "--interactive", is_flag=True)
@click.option("--auth-token")
def list_portfolios(portfolio_id, flatten, show_all, interactive, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    if interactive:
        portfolio_id = prompt_portfolio(
            api.get_portfolios(params={"show_all": True}, headers=headers)
        )
    print(portfolio_id)

    portfolios = api.get_portfolios(
        params={"portfolio_id": portfolio_id, "show_all": show_all},
        headers=headers,
    )

    def flatten_portfolios():
        for portfolio in portfolios:
            if portfolio.parent:
                yield portfolio.parent
            yield portfolio
            for child in portfolio.children:
                yield child

    if flatten:
        portfolios = [p for p in flatten_portfolios()]

    def get_row_value(portfolio: Portfolio):
        return {
            "id": portfolio.id,
            "alias": portfolio.alias,
            "weight": portfolio.weight,
            "parent": portfolio.parent.alias if portfolio.parent else None,
            "children": ", ".join(
                [child.alias for child in portfolio.children]
            ),
            "wallets": ", ".join([w.alias for w in portfolio.wallets]),
        }

    data = list(map(get_row_value, portfolios))

    print(tabulate(data, headers="keys"))


@portfolio.command(name="create")
@click.option("--auth-token")
@click.option("--alias")
@click.option("--weight")
@click.option("--parent-id")
@click.option("--wallet-ids", multiple=True)
def create_portfolio(alias, weight, parent_id, wallet_ids, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    weight and float(weight) / 100

    validate(not_empty_validator, alias)
    validate(
        and_validator(
            [not_empty_validator, number_validator, percent_validator]
        ),
        weight,
    )
    validate(uuid_validator, parent_id)
    validate(and_validator([each_validator(uuid_validator)]), wallet_ids)

    alias_q = {
        "type": "input",
        "name": "alias",
        "message": "Alias",
        "validate": not_empty_validator,
    }
    weight_q = {
        "type": "input",
        "name": "weight",
        "message": "Weight",
        "filter": lambda val: float(val) / 100,
        "validate": and_validator(
            [not_empty_validator, number_validator, percent_validator]
        ),
    }
    has_parent_q = {
        "type": "confirm",
        "name": "has_parent",
        "message": "Has parent",
        "default": False,
    }
    portfolio_q = portfolio_question(
        api.get_portfolios(params={"show_all": True}, headers=headers),
        name="parent_id",
        message="Parent",
        when=lambda answers: answers.get("has_parent"),
    )
    wallet_q = wallets_question(
        api.get_wallets(headers=headers),
        name="wallet_ids",
        message="Wallets",
    )

    questions = [
        *q(alias_q, alias),
        *q(weight_q, weight),
        *q(has_parent_q, parent_id),
        *q(portfolio_q, parent_id),
        *q(wallet_q, wallet_ids),
        confirm_question(when=lambda answers: answers),
    ]

    answers = prompt(questions)

    data = {
        **{
            "alias": alias,
            "weight": weight,
            "parent_id": parent_id,
            "wallet_ids": wallet_ids,
        },
        **answers,
    }

    # remove prompt data
    data.pop("has_parent", None)
    data.pop("continue", None)

    portfolio = api.create_portfolio(data, headers=headers)

    print(portfolio.id)


@portfolio.command(name="balance")
@click.option("-id", "--portfolio-id")
@click.option("-i", "--interactive", is_flag=True)
@click.option("--auth-token")
def show_portfolio_balance(portfolio_id, interactive, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    if interactive:
        portfolio_id = prompt_portfolio(
            api.get_portfolios(
                params={"show_all": True},
                headers=headers,
            )
        )

    result = api.get_portfolios_balance(
        params={"portfolio_id": portfolio_id}, headers=headers
    )

    print(f"{result.balance} {result.currency.acronym}")


@portfolio.command(name="rebalance")
@click.option("-id", "--portfolio-id")
@click.option("--auth-token")
def show_portfolio_rebalance(portfolio_id, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)
    requires_interaction = portfolio_id is None

    if requires_interaction:
        portfolio_id = prompt_portfolio(
            api.get_portfolios(
                params={"show_all": True},
                headers=headers,
            )
        )

    result = api.get_portfolios_rebalance(
        params={"portfolio_id": portfolio_id}, headers=headers
    )

    def get_row_value(change: RebalanceChange):
        return {
            "portfolio": change.portfolio.alias,
            "desired": f"{pp(change.portfolio.weight, percent=True, decimals=0)}%",
            "current": f"{pp(change.weight, percent=True, decimals=2)}%",
            "off_by": f"{pp(change.off_by, percent=True)}%",
            "target": pp(change.target),
            "actual": pp(change.actual),
            "rebalance": f"{change.action.type} {pp(change.action.amount)} {result.currency.acronym}",
        }

    data = list(map(get_row_value, result.changes))

    print(tabulate(data, headers="keys"))
