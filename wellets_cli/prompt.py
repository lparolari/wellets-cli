from typing import List

from InquirerPy import prompt

from wellets_cli.model import Wallet


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
