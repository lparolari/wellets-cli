from typing import List

from PyInquirer import prompt

from wellets_cli.model import Wallet


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

    to_delete = answer["wallet"]

    return list(filter(lambda w: w.alias == to_delete, wallets))[0].id
