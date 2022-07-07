from typing import List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from InquirerPy.prompts import ConfirmPrompt, ListPrompt
from InquirerPy.validator import EmptyInputValidator, NumberValidator

from wellets_cli.model import Currency, Portfolio, Wallet
from wellets_cli.validator import AndValidator, GreaterThanValidator


def confirm_question(message="Confirm", default=True) -> ConfirmPrompt:
    return inquirer.confirm(message, default=default)


def wallet_question(
    wallets: List[Wallet],
    message: str = "Wallet",
    default: Optional[Wallet] = None,
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[Choice(w.id, name=w.alias) for w in wallets],
        default=default and default.id,
    )


def wallets_question(
    wallets: List[Wallet],
    message: str = "Wallets",
    default: List[Wallet] = None,
    allow_none: bool = False,
) -> ListPrompt:
    no_option = (
        [Separator(), Choice(value=None, name="No wallets")]
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


def dollar_rate_question(
    message: str = "Dollar rate", default: Optional[float] = None
):
    return inquirer.number(
        message=message,
        default=default,
        float_allowed=True,
        validate=AndValidator(
            [
                EmptyInputValidator(),
                NumberValidator(float_allowed=True),
                GreaterThanValidator(0),
            ]
        ),
    )


def currency_question(
    currencies: List[Currency],
    message: str = "Currency",
    default: Optional[Currency] = None,
    mandatory=True,
):
    return inquirer.select(
        choices=[
            Choice(w.id, name=f"{w.acronym} - {w.alias}") for w in currencies
        ],
        default=default and default.id,
        message=message,
        mandatory=mandatory,
    )


def change_value_question(
    source_currency: Currency,
    target_currency: Currency = None,
    message: Optional[str] = None,
    default: Optional[float] = None,
):
    from wellets_cli.util import change_from, change_value, pp

    def change_val_transformer(value: str) -> str:
        v = float(value)

        countervalue_in_currency = f"{pp(v)} {target_currency.acronym}"
        countervalue_in_usd = (
            f" ≈ {pp(change_value(change_from(1, v), change_from(1, target_currency.dollar_rate), 1))} USD"
            if target_currency.acronym != "USD"
            else ""
        )
        return f"{countervalue_in_currency}{countervalue_in_usd}"

    return inquirer.number(
        message=message
        or f"Change value (1 {source_currency.acronym} equals ? {target_currency.acronym})",
        float_allowed=True,
        min_allowed=0,
        default=default
        or change_value(
            source_currency.dollar_rate, target_currency.dollar_rate, 1
        ),
        filter=lambda v: (1 / float(v)) * target_currency.dollar_rate,
        transformer=change_val_transformer,
        validate=EmptyInputValidator(),
    )
