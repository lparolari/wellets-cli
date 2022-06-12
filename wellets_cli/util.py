from datetime import datetime

from PyInquirer import prompt


def get_currency_by_id(currencies, currency_id: str) -> str:
    currency_by_id = list(filter(lambda x: x.id == currency_id, currencies))
    return currency_by_id[0]


def make_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


def datetime2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def percent(x: float) -> float:
    return x * 100


def pp(x: float, percent=False, decimals=2) -> str:
    x = x * 100 if percent else x
    return f"{x:.{decimals}f}"

### Converters


def change_from(from_dollar_rate: float, to_dollar_rate: float) -> float:
    return from_dollar_rate / to_dollar_rate


def change_value(
    from_dollar_rate: float, to_dollar_rate: float, value: float
) -> float:
    return 1 / change_from(from_dollar_rate, to_dollar_rate) * value
