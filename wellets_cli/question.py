from typing import List, Union

from wellets_cli.model import Portfolio, Wallet


def q(question, value):
    if value:
        return []
    return [question]


def confirm_question(
    name="continue", message="Confirm", default=True, when=None
):
    if when is None:
        when = lambda _: True

    return {
        "type": "confirm",
        "name": name,
        "message": message,
        "default": default,
        "when": when,
    }


def wallets_question(
    wallets: List[Wallet], name="wallet_id", message="Wallet", when=None
):
    if when is None:
        when = lambda _: True

    def get_wallet_id_by_alias(alias: str) -> Union[str, None]:
        result = list(filter(lambda w: w.alias == alias, wallets))
        if result:
            return result[0].id
        return None

    return {
        "type": "checkbox",
        "name": name,
        "message": message,
        "choices": list(map(lambda w: {"name": w.alias}, wallets)),
        "filter": lambda vals: list(map(get_wallet_id_by_alias, vals)),
        "when": when,
    }


def portfolio_question(
    portfolios: List[Portfolio],
    name="portfolio_id",
    message="Portfolio",
    when=None,
):
    if when is None:
        when = lambda _: True

    def get_portfolio_id_by_alias(alias: str) -> Union[str, None]:
        result = list(filter(lambda w: w.alias == alias, portfolios))
        if result:
            return result[0].id
        return None

    return {
        "type": "list",
        "name": name,
        "message": message,
        "choices": map(lambda p: p.alias, portfolios),
        "filter": get_portfolio_id_by_alias,
        "when": when,
    }
