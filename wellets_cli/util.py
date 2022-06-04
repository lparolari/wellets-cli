def get_currency_acronym_by_id(currencies, currency_id: str) -> str:
    currency_by_id = list(filter(lambda x: x.id == currency_id, currencies))
    return currency_by_id[0].acronym
