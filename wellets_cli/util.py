import re
from datetime import datetime
from typing import List, TypeVar

from dateutil.relativedelta import relativedelta

from wellets_cli.model import Duration

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


def pp(x: float, percent=False, decimals=2, fixed=True) -> str:
    if x is None:
        return ""

    x = x * 100 if percent else x
    p = "%" if percent else ""

    x = f"{x:.{decimals}f}" if fixed else f"{round(x, decimals)}"

    return f"{x}{p}"


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
        name: float(param)
        for name, param in parts.groupdict().items()
        if param
    }

    delta = relativedelta(**duration_params)

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


def change_value(
    from_dollar_rate: float, to_dollar_rate: float, value: float
) -> float:
    return 1 / change_from(from_dollar_rate, to_dollar_rate) * value
