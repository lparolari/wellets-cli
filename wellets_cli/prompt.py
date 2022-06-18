from typing import List

from InquirerPy import prompt

from wellets_cli.model import Portfolio, Wallet


def prompt_confirmation(
    name="continue",
    message="Do you want to continue?",
    default=True,
    when=None,
) -> bool:
    if when is None:
        when = lambda _: True

    question = {
        "type": "confirm",
        "name": name,
        "message": message,
        "default": default,
        "when": when,
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
