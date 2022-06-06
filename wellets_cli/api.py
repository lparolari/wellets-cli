from typing import List

import requests

from wellets_cli.model import Currency, Wallet

BASE_URL = "http://localhost:3333"


class APIError(ValueError):
    pass


def get_currencies(headers: dict) -> List[Currency]:
    response = requests.get(
        f"{BASE_URL}/currencies",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    currencies = response.json()
    currencies = map(lambda c: Currency(**c), currencies)
    currencies = list(currencies)
    return currencies


def get_wallets(headers: dict, params: dict) -> List[Wallet]:
    response = requests.get(
        "http://localhost:3333/wallets",
        headers=headers,
        params=params,
    )

    if not response.ok:
        raise APIError(response.json())

    wallets = response.json()["wallets"]
    wallets = map(lambda w: Wallet(**w), wallets)
    wallets = list(wallets)
    return wallets


def create_wallet(data: dict, headers: dict):
    response = requests.post(
        "http://localhost:3333/wallets",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    wallet = response.json()
    wallet = Wallet(**wallet)
    return wallet
