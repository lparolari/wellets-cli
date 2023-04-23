import re
from datetime import datetime
from typing import List, Optional, TypeVar

from dateutil.relativedelta import relativedelta

import wellets_cli.api as api
from wellets_cli.model import Duration


class Resource:
    id: str


class NamedCurrency:
    acronym: str


T1 = TypeVar("T1", bound=Resource)
T2 = TypeVar("T2", bound=NamedCurrency)


def get_by_id(xs: List[T1], id: str) -> T1:
    return next(filter(lambda x: x.id == id, xs))


def get_currency_by_id(currencies: List[T1], currency_id: str) -> T1:
    currency = list(filter(lambda x: x.id == currency_id, currencies))
    return currency[0]


def get_currency_by_acronym(
    currencies: List[T2], acronym: str, safe=False
) -> Optional[T2]:
    currency = list(filter(lambda x: x.acronym == acronym, currencies))
    if safe and len(currency) == 0:
        return None
    return currency[0]


def make_headers(auth_token: Optional[str]) -> dict:
    if auth_token is None:
        return {}
    return {"Authorization": f"Bearer {auth_token}"}


def datetime2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def percent(x: float) -> float:
    return x * 100


def pp(
    x: float,
    decimals=2,
    percent=False,
    fixed=True,
    with_symbol=False,
    with_rounding=False,
) -> str:
    if x is None:
        return ""  # ignore None values

    # make percentage, if needed
    x = x * 100 if percent else x
    p = "%" if percent and with_symbol else ""

    # round x to given number of decimals
    x_rounded = round(x, decimals)

    # if the number has been rounded, prefix the result with "~" symbol
    # with_rounding eventually disabled rounding indicator
    is_rounded = with_rounding and x_rounded != x
    tilde = "~" if is_rounded else ""

    # format the number with fixed/variable number of decimals
    val = f"{x:.{decimals}f}" if fixed else f"{x_rounded}"

    return f"{tilde}{val}{p}"


def format_duration(duration: Duration) -> str:
    out = ""
    out += f"{duration.years}y " if duration.years else ""
    out += f"{duration.months}M " if duration.months else ""
    out += f"{duration.days}d " if duration.days else ""
    out += f"{duration.hours}h " if duration.hours else ""
    out += f"{duration.minutes}m " if duration.minutes else ""
    out += f"{duration.seconds}s" if duration.seconds else ""
    return out.strip()


duration_regex = re.compile(
    r"^((?P<years>[\.\d]+?)y)? *"
    r"((?P<months>[\.\d]+?)M)? *"
    r"((?P<weeks>[\.\d]+?)w)? *"
    r"((?P<days>[\.\d]+?)d)? *"
    r"((?P<hours>[\.\d]+?)h)? *"
    r"((?P<minutes>[\.\d]+?)m)? *"
    r"((?P<seconds>[\.\d]+?)s)?$"
)


def parse_duration(duration_str: str):
    """
    Parse a time string e.g. '2h 13m' or '1.5d' into a timedelta object.
    Based on Peter's answer at https://stackoverflow.com/a/51916936/2445204
    and virhilo's answer at https://stackoverflow.com/a/4628148/851699

    :param time_str: A string identifying a duration, e.g. '2h13.5m'
    :return datetime.relativedelta: A dateutil.relativedelta.relativedelta object
    """
    parts = duration_regex.match(duration_str)

    if parts is None:
        raise ValueError(
            f"Could not parse duration from '{duration_str}'. Examples of valid strings: '8h', '2d 8h 5m 2s', '2m4.3s'"
        )

    duration_params = {
        name: float(param) for name, param in parts.groupdict().items() if param
    }

    delta = relativedelta(**duration_params)  # type: ignore

    return {
        "years": delta.years,
        "months": delta.months,
        "weeks": 0,  # is internally converted to days by `relativedelta`
        "days": delta.days,
        "hours": delta.hours,
        "minutes": delta.minutes,
        "seconds": delta.seconds,
    }


### Converters


def change_from(from_dollar_rate: float, to_dollar_rate: float) -> float:
    return from_dollar_rate / to_dollar_rate


def change_value(from_dollar_rate: float, to_dollar_rate: float, value: float) -> float:
    return 1 / change_from(from_dollar_rate, to_dollar_rate) * value


def change_val(from_currency, to_currency, value):
    from_dollar_rate = from_currency.dollar_rate
    to_dollar_rate = to_currency.dollar_rate
    return change_value(from_dollar_rate, to_dollar_rate, value)
