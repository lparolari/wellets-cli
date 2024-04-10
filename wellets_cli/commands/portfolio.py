import click
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Portfolio, RebalanceChange
from wellets_cli.question import confirm_question, portfolio_question, wallets_question
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
    """
    Manage portfolios (aka logical collection of wallets).
    """
    pass


@portfolio.command(name="list")
@click.option(
    "--detail",
    is_flag=True,
    help="Show details about children and wallets instead of aggregated information.",
)
@click.option("--auth-token")
def list_portfolios(detail, auth_token):
    """
    List all portfolios.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolios = api.get_portfolios(
        params={"show_all": True},
        headers=headers,
    )

    def pp_children(portfolio: Portfolio):
        if detail:
            return ", ".join(sorted([child.alias for child in portfolio.children]))
        else:
            return (
                f"{len(portfolio.children)} children"
                if len(portfolio.children) > 0
                else ""
            )

    def pp_wallets(portfolio: Portfolio):
        if detail:
            return ", ".join(sorted([wallet.alias for wallet in portfolio.wallets]))
        else:
            return (
                f"{len(portfolio.wallets)} wallets"
                if len(portfolio.wallets) > 0
                else ""
            )

    def pp_alias(portfolio: Portfolio):
        if not portfolio.parent:
            return portfolio.alias
        return f"{pp_alias(portfolio.parent)} > {portfolio.alias}"

    def get_row_value(portfolio: Portfolio):
        alias = pp_alias(portfolio)
        children = pp_children(portfolio)
        wallets = pp_wallets(portfolio)

        return {
            "id": portfolio.id,
            "alias": alias,
            "weight (%)": pp(portfolio.weight, 0, percent=True),
            "parent": portfolio.parent.alias if portfolio.parent else None,
            "children": children,
            "wallets": wallets,
        }

    data = list(map(get_row_value, portfolios))

    print(tabulate(data, headers="keys"))


@portfolio.command(name="show")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("--auth-token")
def show_portfolio(portfolio_id, auth_token):
    """
    Show portfolio details (parent, linked wallets).
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolios = api.get_portfolios(
        params={"portfolio_id": None, "show_all": True},
        headers=headers,
    )
    portfolio_id = portfolio_id or (portfolio_question(portfolios=portfolios).execute())
    portfolio = api.get_portfolio(portfolio_id, headers=headers)

    data = [
        {"key": "id", "value": portfolio.id},
        {"key": "alias", "value": portfolio.alias},
        {"key": "weight", "value": pp(portfolio.weight, 0, percent=True)},
        {
            "key": "parent",
            "value": portfolio.parent.alias if portfolio.parent else "-",
        },
        {
            "key": "children",
            "value": "\n".join(sorted([child.alias for child in portfolio.children]))
            or "-",
        },
        {
            "key": "wallets",
            "value": "\n".join(sorted([w.alias for w in portfolio.wallets])) or "-",
        },
    ]

    print(tabulate(data, headers="keys"))


@portfolio.command(name="create")
@click.option("--auth-token")
@click.option("--alias", type=str)
@click.option("--weight", type=click.FloatRange(0, 100))
@click.option("--parent-id", type=click.UUID)
@click.option(
    "--wallet-ids",
    multiple=True,
    callback=lambda _1, _2, value: validate(each_validator(uuid_validator), value),
)
@click.option("-y", "--yes", is_flag=True, type=bool)
def create_portfolio(alias, weight, parent_id, wallet_ids, auth_token, yes):
    """
    Create a new portfolio.
    """
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
        wallet_ids or wallets_question(wallets=wallets, allow_none=True).execute()
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
    callback=lambda _1, _2, value: validate(each_validator(uuid_validator), value),
)
@click.option("-y", "--yes", is_flag=True, type=bool)
def edit_portfolio(portfolio_id, alias, weight, parent_id, wallet_ids, auth_token, yes):
    """
    Edit an existing portfolio.
    """
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
    """
    Delete an existing portfolio.

    This will NOT affect your registered wallets, transactions and assets.
    """
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
@click.option("--auth-token")
def show_portfolio_balance(portfolio_id, auth_token):
    """
    Show the total balance of a portfolio.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            portfolios=api.get_portfolios(
                params={"show_all": True},
                headers=headers,
            )
        ).execute()
    )

    result = api.get_portfolios_balance(
        params={"portfolio_id": portfolio_id}, headers=headers
    )

    print(f"{result.currency.acronym} {pp(result.balance)}")


@portfolio.command(name="rebalance")
@click.option("-id", "--portfolio-id", type=click.UUID)
@click.option("--auth-token")
def show_portfolio_rebalance(portfolio_id, auth_token):
    """
    Show the operation to perform on a portfolio to rebalance it.

    Rebalancing a portfolio is required to keep the desired exposition on each asset.
    Rebalancing is computed by weighting the countervalues in your base currency of
    the children and comparing it to the desired allocation weight.
    """
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolio_id = (
        portfolio_id
        or portfolio_question(
            portfolios=api.get_portfolios(
                params={"show_all": True},
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
            "desired (%)": f"{pp(change.portfolio.weight, 0, percent=True)}",
            "current (%)": pp(change.weight, 1, percent=True),
            "off_by (%)": pp(change.off_by, 1, percent=True),
            "target": pp(change.target),
            "actual": pp(change.actual),
            "rebalance": f"{change.action.type} {pp(change.action.amount)} {result.currency.acronym}",
        }

    data = list(map(get_row_value, result.changes))

    print(tabulate(data, headers="keys"))
