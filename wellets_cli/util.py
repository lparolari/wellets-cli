from PyInquirer import prompt


def get_currency_acronym_by_id(currencies, currency_id: str) -> str:
    currency_by_id = list(filter(lambda x: x.id == currency_id, currencies))
    return currency_by_id[0].acronym


def confirm():
    question = {
        "type": "confirm",
        "message": "Do you want to continue?",
        "name": "continue",
        "default": True,
    }

    answers = prompt([question])

    return answers["continue"]
