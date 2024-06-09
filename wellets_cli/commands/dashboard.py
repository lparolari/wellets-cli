import click
from tabulate import tabulate

import wellets_cli.api as api
from wellets_cli.auth import get_auth_token, get_email
from wellets_cli.model import Asset, Wallet
from wellets_cli.util import change_val, change_value, get_by_id, make_headers, pp


@click.command(help="Show dashboard.")
@click.option("--auth-token")
def dashboard(auth_token):
    auth_token = auth_token or get_auth_token()
    headers = make_headers(auth_token)

    username = get_email()
    currency = api.get_preferred_currency(headers=headers)
    total_balance = api.get_total_balance(headers=headers)
    assets = api.get_assets(headers=headers)
    portfolios = api.get_portfolios(params={"show_all": True}, headers=headers)
    wallets = api.get_wallets(headers=headers)

    click.echo(f"Welcome, {username}!")
    click.echo()

    click.echo(f"Total balance = {currency.acronym} {pp(total_balance.balance)}")
    click.echo()

    a_names = tabulate([{"asset": a.currency.acronym} for a in assets], headers="keys")
    p_names = tabulate([{"portfolio": p.alias} for p in portfolios], headers="keys")
    w_names = tabulate([{"wallet": w.alias} for w in wallets if w.balance > 0], headers="keys")

    click.echo(_append_horizontal(a_names, p_names, w_names, gutter=5))
    click.echo()

    click.echo(click.style("Assets", bold=True))

    a_data = [
        {
            "asset": a.currency.acronym,
            "balance": pp(a.balance),
            "equivalent": f"{currency.acronym} {pp(change_val(a.currency, currency, a.balance))}",
        }
        for a in assets
    ]

    click.echo(tabulate(a_data, headers="keys"))
    click.echo()

    click.echo(click.style("Portfolios", bold=True))

    p_data = [
        {
            "portfolio": p.alias,
            "weight (%)": pp(p.weight, 0, percent=True),
        }
        for p in portfolios
    ]

    click.echo(tabulate(p_data, headers="keys"))
    click.echo()

    click.echo(click.style("Wallets", bold=True))

    w_data = [
        {
            "alias": w.alias,
            "balance": f"{w.currency.acronym} {pp(w.balance)}",
            "equivalent": f"{currency.acronym} {pp(change_val(w.currency, currency, w.balance))}",
        }
        for w in wallets
        if w.balance > 0
    ]

    click.echo(tabulate(w_data, headers="keys"))


def _append_horizontal(*args, gutter=1):
    """
    Append strings horizontally with a gutter between them.
    """

    def _append_horizontal_binary(x: str, y: str, gutter=1):
        x_lines = x.splitlines()
        y_lines = y.splitlines()

        # x_lines and y_lines must be extended to the same length
        x_lines.extend([""] * max(len(y_lines) - len(x_lines), 0))
        y_lines.extend([""] * max(len(x_lines) - len(y_lines), 0))

        max_x_len = max(len(line) for line in x_lines)
        gutter_str = " " * gutter
        return "\n".join(
            f"{x_line.ljust(max_x_len)}{gutter_str}{y_line}"
            for x_line, y_line in zip(x_lines, y_lines)
        )

    from functools import reduce

    return reduce(lambda x, y: _append_horizontal_binary(x, y, gutter), args)
