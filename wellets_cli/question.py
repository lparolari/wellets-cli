from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple

import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice, Separator
from InquirerPy.prompts import ConfirmPrompt, InputPrompt, ListPrompt, NumberPrompt
from InquirerPy.validator import EmptyInputValidator, NumberValidator

from wellets_cli.model import (
    Accumulation,
    Asset,
    Currency,
    Portfolio,
    Transaction,
    Wallet,
)
from wellets_cli.util import parse_duration
from wellets_cli.validator import (
    AndValidator,
    DateValidator,
    DurationValidator,
    GreaterThanValidator,
)


def warning_message(message="") -> str:
    return click.style(message, fg="yellow")


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
    default: Optional[List[Wallet]] = None,
    allow_none: bool = False,
) -> ListPrompt:
    no_option = (
        [Separator(), Choice(value=None, name="No wallets")] if allow_none else []
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
        [Separator(), Choice(value=None, name="No parent")] if allow_none else []
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
        choices=[Choice(w.id, name=f"{w.acronym} - {w.alias}") for w in currencies],
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
        or change_value(source_currency.dollar_rate, target_currency.dollar_rate, 1),
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
        [Separator(), Choice(value=None, name="No accumulation")] if allow_none else []
    )

    return inquirer.select(
        message=message,
        choices=[Choice(a.id, name=a.alias) for a in accumulations]
        + no_option,  # type: ignore
        default=default and default.id,
    )


def date_question(
    message: str = "Date",
    default: Optional[datetime] = None,
    date_fmt="%Y-%m-%d %H:%M",
) -> InputPrompt:
    return inquirer.text(
        message=message,
        default=default.strftime(date_fmt) if default else "",
        validate=AndValidator(
            [EmptyInputValidator(), DateValidator(date_fmt=date_fmt)]
        ),
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


def interval_question(
    message: str = "Interval",
    choices: List[str] = ["1h", "1d", "1w", "1M", "1y"],
    default: Optional[str] = None,
) -> ListPrompt:
    return inquirer.select(
        message=message,
        choices=[Choice(i, name=i) for i in choices],
        default=default,
    )


def date_range_question(
    message: str = "Range",
    now: Optional[datetime] = None,
    default: Optional[Tuple[datetime, datetime]] = None,
    date_fmt: Optional[str] = None,
) -> Any:
    class DateRangePrompt:
        def __init__(
            self,
            message: str,
            now: Optional[datetime] = None,
            default: Optional[Tuple[datetime, datetime]] = None,
            date_fmt: Optional[str] = None,
        ):
            self._message = message
            self._now = now or datetime.now()
            self._date_fmt = "%Y-%m-%d" if date_fmt is None else date_fmt
            self._default = default
            self._make_predefined_ranges()
            self._make_default()

        def execute(self) -> Any:
            choices = (
                [Choice(value, name) for (name, value) in self.predefined_ranges]
                + [Separator()]  # type: ignore
                + [Choice(None, "Custom")]
            )

            the_range = inquirer.select(
                message,
                choices,
                default=self._default,
            ).execute()

            if the_range is None:
                return self._custom_range()

            return the_range

        def _custom_range(self):
            start = date_question(
                message="Start date",
                default=self._now,
                date_fmt=self._date_fmt,
            ).execute()

            end = date_question(
                message="End date",
                default=self._now,
                date_fmt=self._date_fmt,
            ).execute()

            return (start, end)

        def _make_predefined_ranges(self):
            self.last_1d = (self._now - timedelta(days=1), self._now)
            self.last_7d = (self._now - timedelta(days=7), self._now)
            self.last_30d = (self._now - timedelta(days=30), self._now)
            self.last_90d = (self._now - timedelta(days=90), self._now)
            self.last_180d = (self._now - timedelta(days=180), self._now)
            self.last_365d = (self._now - timedelta(days=365), self._now)

            self.predefined_ranges = [
                ("Last day", self.last_1d),
                ("Last 7 days", self.last_7d),
                ("Last 30 days", self.last_30d),
                ("Last 90 days", self.last_90d),
                ("Last 180 days", self.last_180d),
                ("Last 365 days", self.last_365d),
            ]

        def _make_default(self):
            if self._default is None:
                self._default = self.last_365d

    return DateRangePrompt(message, now, default, date_fmt)
