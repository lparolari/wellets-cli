from datetime import datetime
from typing import Any, Generic, List, TypeVar

from InquirerPy import prompt

T = TypeVar("T")


def get_by_id(xs: List[T], id: str) -> T:
    return next(filter(lambda x: x.id == id, xs))


def get_currency_by_id(currencies: List[T], currency_id: str) -> T:
    currency = list(filter(lambda x: x.id == currency_id, currencies))
    return currency[0]


def get_currency_by_acronym(
    currencies: List[T], acronym: str, safe=False
) -> T:
    currency = list(filter(lambda x: x.acronym == acronym, currencies))
    if safe and len(currency) == 0:
        return None
    return currency[0]


def make_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


def datetime2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def percent(x: float) -> float:
    return x * 100


def pp(x: float, percent=False, decimals=2) -> str:
    if x is None:
        return ""

    x = x * 100 if percent else x
    p = "%" if percent else ""

    return f"{x:.{decimals}f}{p}"


### Converters


def change_from(from_dollar_rate: float, to_dollar_rate: float) -> float:
    return from_dollar_rate / to_dollar_rate


def change_value(
    from_dollar_rate: float, to_dollar_rate: float, value: float
) -> float:
    return 1 / change_from(from_dollar_rate, to_dollar_rate) * value
