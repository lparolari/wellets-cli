import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token
from wellets_cli.model import Portfolio
from wellets_cli.util import make_headers


@click.group()
def portfolio():
    pass


@portfolio.command(name="list")
@click.option("--portfolio-id")
@click.option("--flatten", is_flag=True)
@click.option("--all", "show_all", is_flag=True)
@click.option("--auth-token")
def list_portfolios(portfolio_id, flatten, show_all, auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    portfolios = api.get_portfolios(
        portfolio_id, params={"show_all": show_all}, headers=headers
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
