from typing import Callable, List, Optional, Union

from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from InquirerPy.prompts import ConfirmPrompt, InputPrompt, ListPrompt

from wellets_cli.model import Portfolio, Wallet


def q(question, value):
    if value:
        return []
    return [question]


def confirm_question(message="Confirm", default=True) -> ConfirmPrompt:
    return inquirer.confirm(message, default=default)


def wallets_question(
    wallets: List[Wallet],
    message: str = "Wallets",
    default: List[Wallet] = None,
) -> ListPrompt:

    return inquirer.select(
        message=message,
        choices=[
            Choice(w.id, name=w.alias, enabled=default and w in default)
            for w in wallets
        ],
        multiselect=True,
    )


def portfolio_question(
    portfolios: List[Portfolio],
    message: str = "Portfolio",
    default: Optional[Portfolio] = None,
    allow_none: bool = False,
) -> ListPrompt:
    no_option = (
        [Separator(), Choice(value=None, name="No parent")]
        if allow_none
        else []
    )

    return inquirer.select(
        message=message,
        choices=[
            Choice(p.id, name=p.alias, enabled=default and default == p)
            for p in portfolios
        ]
        + no_option,
        default=default and default.id,
    )
