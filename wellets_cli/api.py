from typing import List

import requests

from wellets_cli.model import (
    Currency,
    UserSettings,
    Wallet,
    WalletAverageLoadPrice,
)

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


def create_wallet(data: dict, headers: dict) -> Wallet:
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


def delete_wallet(wallet_id: str, headers: dict) -> Wallet:
    response = requests.delete(
        f"{BASE_URL}/wallets/{wallet_id}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    wallet = response.json()
    wallet = Wallet(**wallet)
    return wallet


def get_wallet_average_load_price(
    wallet_id: str, headers: dict
) -> WalletAverageLoadPrice:
    response = requests.get(
        f"{BASE_URL}/wallets/{wallet_id}/average-load-price",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    avg_load_price = response.json()
    avg_load_price = WalletAverageLoadPrice(**avg_load_price)
    return avg_load_price


def get_user_settings(headers: dict) -> UserSettings:
    response = requests.get(
        f"{BASE_URL}/users/settings",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    user_settings = response.json()
    user_settings = UserSettings(**user_settings)
    return user_settings


def get_preferred_currency(headers: dict) -> Currency:
    user_settings = get_user_settings(headers=headers)
    return user_settings.currency
