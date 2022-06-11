from typing import List, Optional

import requests

from wellets_cli.auth import UserSession
from wellets_cli.model import (
    Balance,
    Portfolio,
    UserCurrency,
    UserSettings,
    Wallet,
    WalletAverageLoadPrice,
)

BASE_URL = "http://localhost:3333"


class APIError(ValueError):
    pass


def login(email: str, password: str) -> UserSession:
    response = requests.post(
        f"{BASE_URL}/users/sessions",
        json={"email": email, "password": password},
    )

    if not response.ok:
        raise APIError(response.json())

    user_session = response.json()
    user_session = UserSession(**user_session)
    return user_session


def get_currencies(headers: dict) -> List[UserCurrency]:
    response = requests.get(
        f"{BASE_URL}/currencies",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    currencies = response.json()
    currencies = map(lambda c: UserCurrency(**c), currencies)
    currencies = list(currencies)
    return currencies


def get_wallets(headers: dict, params: Optional[dict] = None) -> List[Wallet]:
    response = requests.get(
        f"{BASE_URL}/wallets",
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
        f"{BASE_URL}/wallets",
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


def get_preferred_currency(headers: dict) -> UserCurrency:
    user_settings = get_user_settings(headers=headers)
    return user_settings.currency


def get_portfolios(
    portfolio_id: str, params: dict, headers: dict
) -> List[Portfolio]:
    show_all = params["show_all"]

    response = requests.get(
        f"{BASE_URL}/portfolios"
        f"/{portfolio_id if portfolio_id else ''}"
        f"{'/all' if show_all else ''}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    portfolios = response.json()
    portfolios = map(lambda w: Portfolio(**w), portfolios)
    portfolios = list(portfolios)
    return portfolios


def get_wallet_balance(wallet_id: str, headers: dict) -> Balance:
    response = requests.get(
        f"{BASE_URL}/wallets/balance",
        params={"wallet_id": wallet_id},
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance


def get_total_balance(headers: dict) -> Balance:
    response = requests.get(
        f"{BASE_URL}/wallets/total-balance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance


def get_wallets_total_balance(headers: dict) -> Balance:
    response = requests.get(
        f"{BASE_URL}/wallets/total-balance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance
