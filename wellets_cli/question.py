from datetime import datetime
from typing import List, Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from InquirerPy.prompts import (
    ConfirmPrompt,
    InputPrompt,
    ListPrompt,
    NumberPrompt,
)
from InquirerPy.validator import EmptyInputValidator, NumberValidator

from wellets_cli.model import (
    Accumulation,
    Asset,
    Currency,
    Investment,
    Portfolio,
    Transaction,
    Wallet,
)
from wellets_cli.util import get_by_id, parse_duration
from wellets_cli.validator import (
    AndValidator,
    DateValidator,
    DurationValidator,
    GreaterThanOrEqualValidator,
    GreaterThanValidator,
)


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
            Choice(
                w.id,
                name=w.alias,
                enabled=default is not None and w in default,
            )
            for w in wallets
        ]
        + no_option,  # type: ignore
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
            Choice(
                p.id,
                name=p.alias,
                enabled=default is not None and default == p,
            )
            for p in portfolios
        ]
        + no_option,  # type: ignore
        default=default and default.id,
    )


def dollar_rate_question(
    message: str = "Dollar rate", default: Optional[float] = None
) -> NumberPrompt:
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
) -> ListPrompt:
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
    target_currency: Currency,
    message: Optional[str] = None,
    default: Optional[float] = None,
) -> NumberPrompt:
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


def accumulation_question(
    accumulations: List[Accumulation],
    message: str = "Accumulation",
    default: Optional[Accumulation] = None,
    allow_none: bool = False,
) -> ListPrompt:
    no_option = (
        [Separator(), Choice(value=None, name="No accumulation")]
        if allow_none
        else []
    )

    return inquirer.select(
        message=message,
        choices=[Choice(a.id, name=a.alias) for a in accumulations]
        + no_option,  # type: ignore
        default=default and default.id,
    )


def date_question(
    message: str = "Date (yyyy-MM-dd HH:mm)",
    default: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M"),
) -> InputPrompt:
    return inquirer.text(
        message=message,
        default=default if default else "",
        validate=AndValidator([EmptyInputValidator(), DateValidator()]),
    )


def duration_question(
    message: str = "Duration",
) -> InputPrompt:
    return inquirer.text(
        message=message,
        validate=AndValidator([EmptyInputValidator(), DurationValidator()]),
        filter=lambda x: parse_duration(x),
    )


def asset_question(
    assets: List[Asset],
    message: str = "Asset",
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[Choice(a.id, name=a.currency.acronym) for a in assets],
    )


def transaction_question(
    transactions: List[Transaction],
    message: str = "Transaction",
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[Choice(t.id, name=t.description) for t in transactions],
    )


def transactions_question(
    transactions: List[Transaction],
    message: str = "Transaction",
) -> ListPrompt:
    return inquirer.select(
        message=message,
        multiselect=True,
        choices=[Choice(t.id, name=t.description) for t in transactions],
    )


def investment_question(
    investments: List[Investment],
    message: str = "Investment",
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[Choice(i.id, name=i.alias) for i in investments],
    )


def investment_entry_question(
    wallets: List[Wallet], currencies: List[Currency]
):
    class InvestmentEntryPrompt:
        def execute(self):
            kind = inquirer.select(
                message="Type",
                choices=[
                    Choice("input", name="Input"),
                    Choice("output", name="Output"),
                ],
            ).execute()

            wallet_id = wallet_question(wallets).execute()
            wallet = get_by_id(wallets, wallet_id)
            wallet_currency = get_by_id(currencies, wallet.currency_id)

            value = inquirer.number(
                message="Amount",
                float_allowed=True,
                validate=AndValidator(
                    [EmptyInputValidator(), GreaterThanOrEqualValidator(0)]
                ),
                filter=lambda x: float(x),
            ).execute()

            currency_id = currency_question(
                currencies=currencies, message="Change rate"
            ).execute()
            currency = get_by_id(currencies, currency_id)

            change_val = change_value_question(
                source_currency=wallet_currency,
                target_currency=currency,
            ).execute()

            input_id = None

            if kind == "output":
                # input_id = inquirer.select(
                #     message="Input",
                #     choices=[Choice(i.id, name="foo") for i in entries]
                # ).execute()
                raise NotImplementedError("Not implemented yet")

            return {
                "wallet_id": wallet_id,
                "value": value,
                "dollar_rate": change_val,
                "input_id": input_id,
            }

    return InvestmentEntryPrompt()
