import click
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Portfolio, RebalanceChange
from wellets_cli.question import (
    confirm_question,
    portfolio_question,
    wallets_question,
)
from wellets_cli.util import make_headers, pp
from wellets_cli.validator import (
    AndValidator,
    GreaterThanOrEqualValidator,
    LessThanOrEqualValidator,
    NumberValidator,
    each_validator,
    uuid_validator,
    validate,
)


@click.group()
def portfolio():
    pass


@portfolio.command(name="list")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("-f", "--flatten", is_flag=True)
@click.option("-a", "--all", "show_all", is_flag=True)
@click.option("-i", "--interactive", is_flag=True)
@click.option("--auth-token")
def list_portfolios(portfolio_id, flatten, show_all, interactive, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = portfolio_id or (
        interactive
        and portfolio_question(
            portfolios=api.get_portfolios(
                params={"show_all": True},
                headers=headers,
            )
        ).execute()
    )

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
            "weight": pp(portfolio.weight, percent=True, decimals=0),
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
@click.option("--alias", type=str)
@click.option("--weight", type=click.FloatRange(0, 100))
@click.option("--parent-id", type=click.UUID)
@click.option(
    "--wallet-ids",
    multiple=True,
    callback=lambda _1, _2, value: validate(
        each_validator(uuid_validator), value
    ),
)
@click.option("-y", "--yes", is_flag=True, type=bool)
def create_portfolio(alias, weight, parent_id, wallet_ids, auth_token, yes):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    weight = weight and float(weight) / 100

    portfolios = api.get_portfolios(params={"show_all": True}, headers=headers)
    wallets = api.get_wallets(headers=headers)

    alias = (
        alias
        or inquirer.text(
            message="Alias",
            validate=EmptyInputValidator(),
        ).execute()
    )
    weight = (
        weight
        or inquirer.number(
            message="Weight",
            float_allowed=True,
            min_allowed=0,
            max_allowed=100,
            validate=EmptyInputValidator(),
            filter=lambda v: float(v) / 100,
        ).execute()
    )
    parent_id = (
        parent_id
        or portfolio_question(
            portfolios=portfolios,
            message="Parent",
            allow_none=True,
        ).execute()
    )
    wallet_ids = (
        wallet_ids
        or wallets_question(wallets=wallets, allow_none=True).execute()
    )

    data = {
        "alias": alias,
        "weight": weight,
        "parent_id": parent_id,
        "wallet_ids": wallet_ids,
    }

    if not yes and not confirm_question().execute():
        return

    portfolio = api.create_portfolio(data, headers=headers)

    print(portfolio.id)


@portfolio.command(name="edit")
@click.option("--auth-token")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("--alias", type=str)
@click.option("--weight", type=click.FloatRange(0, 100))
@click.option("--parent-id", type=click.UUID)
@click.option(
    "--wallet-ids",
    multiple=True,
    callback=lambda _1, _2, value: validate(
        each_validator(uuid_validator), value
    ),
)
@click.option("-y", "--yes", is_flag=True, type=bool)
def edit_portfolio(
    portfolio_id, alias, weight, parent_id, wallet_ids, auth_token, yes
):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    weight = weight and float(weight) / 100

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            api.get_portfolios(params={"show_all": True}, headers=headers),
            message="Portfolio",
        ).execute()
    )

    portfolio = api.get_portfolio(portfolio_id, headers=headers)
    portfolios = api.get_portfolios(params={"show_all": True}, headers=headers)
    wallets = api.get_wallets(headers=headers)

    alias = (
        alias
        or inquirer.text(
            message="Alias",
            default=portfolio.alias,
            validate=EmptyInputValidator(),
        ).execute()
    )
    weight = (
        weight
        or inquirer.number(
            message="Weight",
            float_allowed=True,
            validate=AndValidator(
                [
                    EmptyInputValidator(),
                    NumberValidator(float_allowed=True),
                    GreaterThanOrEqualValidator(0),
                    LessThanOrEqualValidator(100),
                ]
            ),
            default=portfolio.weight * 100,
            filter=lambda v: float(v) / 100,
        ).execute()
    )
    parent_id = (
        parent_id
        or portfolio_question(
            portfolios=portfolios,
            default=portfolio.parent,
            message="Parent",
            allow_none=True,
        ).execute()
    )
    wallet_ids = (
        wallet_ids
        or wallets_question(
            wallets=wallets, default=portfolio.wallets, allow_none=True
        ).execute()
    )

    data = {
        "alias": alias,
        "weight": weight,
        "parent_id": parent_id,
        "wallet_ids": wallet_ids,
    }

    if not yes and not confirm_question().execute():
        return

    portfolio = api.edit_portfolio(portfolio_id, data, headers=headers)

    print(portfolio.id)


@portfolio.command(name="delete")
@click.option("--auth-token")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("-y", "--yes", is_flag=True, type=bool)
def delete_portfolio(portfolio_id, auth_token, yes):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            api.get_portfolios(params={"show_all": True}, headers=headers),
            message="Portfolio",
        ).execute()
    )

    if not yes and not confirm_question().execute():
        return

    api.delete_portfolio(portfolio_id, headers=headers)

    print(portfolio_id)


@portfolio.command(name="balance")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("-a", "--show-all", is_flag=True, default=False)
@click.option("--auth-token")
def show_portfolio_balance(portfolio_id, show_all, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            portfolios=api.get_portfolios(
                params={"show_all": show_all},
                headers=headers,
            )
        ).execute()
    )

    result = api.get_portfolios_balance(
        params={"portfolio_id": portfolio_id}, headers=headers
    )

    print(f"{result.balance} {result.currency.acronym}")


@portfolio.command(name="rebalance")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("-a", "--show-all", is_flag=True, default=False)
@click.option("--auth-token")
def show_portfolio_rebalance(portfolio_id, show_all, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            portfolios=api.get_portfolios(
                params={"show_all": show_all},
                headers=headers,
            )
        ).execute()
    )

    result = api.get_portfolios_rebalance(
        params={"portfolio_id": portfolio_id}, headers=headers
    )

    def get_row_value(change: RebalanceChange):
        return {
            "portfolio": change.portfolio.alias,
            "desired": f"{pp(change.portfolio.weight, percent=True, decimals=0)}",
            "current": pp(change.weight, percent=True, decimals=2),
            "off_by": pp(change.off_by, percent=True),
            "target": pp(change.target),
            "actual": pp(change.actual),
            "rebalance": f"{change.action.type} {pp(change.action.amount)} {result.currency.acronym}",
        }

    data = list(map(get_row_value, result.changes))

    print(tabulate(data, headers="keys"))
