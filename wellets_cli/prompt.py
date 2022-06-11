from typing import List

from PyInquirer import prompt

from wellets_cli.model import Portfolio, Wallet


def prompt_confirmation() -> bool:
    question = {
        "type": "confirm",
        "message": "Do you want to continue?",
        "name": "continue",
        "default": True,
    }

    answers = prompt([question])

    return answers["continue"]


def prompt_wallet(wallets: List[Wallet]) -> str:
    questions = [
        {
            "type": "list",
            "name": "wallet",
            "message": "Wallet",
            "choices": map(lambda w: w.alias, wallets),
        }
    ]

    answer = prompt(questions)

    wallet_alias = answer["wallet"]

    return list(filter(lambda w: w.alias == wallet_alias, wallets))[0].id


def prompt_portfolio(portfolios: List[Portfolio]) -> str:
    questions = [
        {
            "type": "list",
            "name": "portfolio",
            "message": "Portfolio",
            "choices": map(lambda p: p.alias, portfolios),
        }
    ]

    answer = prompt(questions)

    portfolio_alias = answer["portfolio"]

    return list(filter(lambda p: p.alias == portfolio_alias, portfolios))[0].id
