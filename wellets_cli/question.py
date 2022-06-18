from typing import List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from InquirerPy.prompts import ConfirmPrompt, ListPrompt

from wellets_cli.model import Portfolio, Wallet


def confirm_question(message="Confirm", default=True) -> ConfirmPrompt:
    return inquirer.confirm(message, default=default)


def wallet_question(
    wallets: List[Wallet],
    message: str = "Wallet",
    default: Optional[Wallet] = None,
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[
            Choice(w.id, name=w.alias)
            for w in wallets
        ],
        default=default and default.id,
    )


def wallets_question(
    wallets: List[Wallet],
    message: str = "Wallets",
    default: List[Wallet] = None,
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
            Choice(w.id, name=w.alias, enabled=default and w in default)
            for w in wallets
        ]
        + no_option,
        multiselect=True,
        filter=lambda xs: [x for x in xs if x is not None],
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
