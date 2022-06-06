from PyInquirer import prompt


def get_currency_by_id(currencies, currency_id: str) -> str:
    currency_by_id = list(filter(lambda x: x.id == currency_id, currencies))
    return currency_by_id[0]


def confirm():
    question = {
        "type": "confirm",
        "message": "Do you want to continue?",
        "name": "continue",
        "default": True,
    }

    answers = prompt([question])

    return answers["continue"]



### Converters

def change_from(from_dollar_rate: float, to_dollar_rate: float) -> float:
    return from_dollar_rate / to_dollar_rate

def change_value(from_dollar_rate: float, to_dollar_rate: float, value: float) -> float:
    return 1 / change_from(from_dollar_rate, to_dollar_rate) * value
