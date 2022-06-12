import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Portfolio, RebalanceChange
from wellets_cli.prompt import prompt_portfolio
from wellets_cli.util import make_headers, percent, pp


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
        }

    data = list(map(get_row_value, portfolios))

    print(tabulate(data, headers="keys"))


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
