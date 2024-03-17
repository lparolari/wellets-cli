from typing import List, Optional

import requests

from wellets_cli.auth import UserSession
from wellets_cli.config import settings
from wellets_cli.model import (
    Accumulation,
    Asset,
    AssetAllocation,
    AssetBalance,
    AssetHistory,
    AverageLoadPrice,
    Balance,
    CapitalGain,
    Currency,
    Investment,
    KLines,
    NextAccumulationEntry,
    Portfolio,
    PortfolioRebalance,
    Transaction,
    Transfer,
    User,
    UserCurrency,
    UserSettings,
    Wallet,
    WalletAverageLoadPrice,
    WalletHistory,
)

base_url = lambda: settings.api_url


class APIError(ValueError):
    def __str__(self) -> str:
        if len(self.args) != 0 and "message" in self.args[0]:
            return self.args[0]["message"]
        return super().__str__()


def login(email: str, password: str) -> UserSession:
    response = requests.post(
        f"{base_url()}/users/sessions",
        json={"email": email, "password": password},
    )

    if not response.ok:
        raise APIError(response.json())

    user_session = response.json()
    user_session = UserSession(**user_session)
    return user_session


def get_currencies(headers: dict) -> List[UserCurrency]:
    response = requests.get(
        f"{base_url()}/currencies",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    currencies = response.json()
    currencies = map(lambda c: UserCurrency(**c), currencies)
    currencies = list(currencies)
    return currencies


def sync_currencies(headers: dict) -> str:
    response = requests.post(
        f"{base_url()}/currencies/rate/sync",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    if response.status_code == 201:
        return "synced"
    if response.status_code == 200:
        return "already synced"
    return "unknown"


def get_wallets(headers: dict, params: Optional[dict] = None) -> List[Wallet]:
    response = requests.get(
        f"{base_url()}/wallets",
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
        f"{base_url()}/wallets",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    wallet = response.json()
    wallet = Wallet(**wallet)
    return wallet


def update_wallet(wallet_id, data: dict, headers: dict) -> Wallet:
    response = requests.patch(
        f"{base_url()}/wallets/{wallet_id}",
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
        f"{base_url()}/wallets/{wallet_id}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    wallet = response.json()
    wallet = Wallet(**wallet)
    return wallet


def get_wallet_average_load_price(
    params: dict, headers: dict
) -> WalletAverageLoadPrice:
    response = requests.get(
        f"{base_url()}/wallets/average-load-price",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    avg_load_price = response.json()
    avg_load_price = WalletAverageLoadPrice(**avg_load_price)
    return avg_load_price


def get_user_settings(headers: dict) -> UserSettings:
    response = requests.get(
        f"{base_url()}/users/settings",
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


def get_portfolios(params: dict, headers: dict) -> List[Portfolio]:
    portfolio_id = params.get("portfolio_id")
    show_all = params.get("show_all")

    response = requests.get(
        f"{base_url()}/portfolios"
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


def get_portfolio(portfolio_id: str, headers: dict) -> Portfolio:
    response = requests.get(
        f"{base_url()}/portfolios/{portfolio_id}/details",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    portfolio = response.json()
    portfolio = Portfolio(**portfolio)
    return portfolio


def create_portfolio(data: dict, headers: dict) -> Portfolio:
    response = requests.post(
        f"{base_url()}/portfolios",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    portfolio = response.json()
    portfolio = Portfolio(**portfolio)
    return portfolio


def edit_portfolio(portfolio_id: str, data: dict, headers: dict) -> Portfolio:
    response = requests.put(
        f"{base_url()}/portfolios/{portfolio_id}",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    portfolio = response.json()
    portfolio = Portfolio(**portfolio)
    return portfolio


def delete_portfolio(portfolio_id: str, headers: dict) -> Portfolio:
    response = requests.delete(
        f"{base_url()}/portfolios/{portfolio_id}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    portfolio = response.json()
    portfolio = Portfolio(**portfolio)
    return portfolio


def get_wallet_balance(wallet_id: str, headers: dict) -> Balance:
    response = requests.get(
        f"{base_url()}/wallets/balance",
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
        f"{base_url()}/wallets/total-balance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance


def get_wallets_total_balance(headers: dict) -> Balance:
    response = requests.get(
        f"{base_url()}/wallets/total-balance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance


def get_portfolios_balance(params: dict, headers: dict) -> Balance:
    response = requests.get(
        f"{base_url()}/portfolios/balance",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = Balance(**balance)
    return balance


def get_portfolios_rebalance(params: dict, headers: dict) -> PortfolioRebalance:
    portfolio_id = params["portfolio_id"]

    response = requests.get(
        f"{base_url()}/portfolios/{portfolio_id}/rebalance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    rebalance = response.json()
    rebalance = PortfolioRebalance(**rebalance)
    return rebalance


def get_transactions(params: dict, headers: dict) -> List[Transaction]:
    response = requests.get(
        f"{base_url()}/transactions/",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    transactions = response.json()["transactions"]
    transactions = [Transaction(**t) for t in transactions]
    return transactions


def create_transaction(data: dict, headers: dict) -> Transaction:
    response = requests.post(
        f"{base_url()}/transactions",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    transaction = response.json()
    transaction = Transaction(**transaction)
    return transaction


def get_wallet(wallet_id: str, headers: dict) -> Wallet:
    response = requests.get(
        f"{base_url()}/wallets/{wallet_id}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    wallet = response.json()
    wallet = Wallet(**wallet)
    return wallet


def get_accumulations(params: dict, headers: dict) -> List[Accumulation]:
    response = requests.get(
        f"{base_url()}/accumulations/",
        headers=headers,
        params=params,
    )

    if not response.ok:
        raise APIError(response.json())

    accumulations = response.json()
    accumulations = [Accumulation(**a) for a in accumulations]
    return accumulations


def get_next_accumulation_entry(
    accumulation_id: str, headers: dict
) -> NextAccumulationEntry:
    response = requests.get(
        f"{base_url()}/accumulations/{accumulation_id}/next-entry",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    entry = response.json()
    entry = NextAccumulationEntry(**entry)
    return entry


def create_accumulation(data: dict, headers: dict) -> Accumulation:
    response = requests.post(
        f"{base_url()}/accumulations",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    accumulation = response.json()
    accumulation = Accumulation(**accumulation)
    return accumulation


def delete_accumulation(accumulation_id: str, headers: dict) -> Accumulation:
    response = requests.delete(
        f"{base_url()}/accumulations/{accumulation_id}",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    accumulation = response.json()
    accumulation = Accumulation(**accumulation)
    return accumulation


def create_transfer(data: dict, headers: dict) -> Transfer:
    response = requests.post(
        f"{base_url()}/transfers",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    transfer = response.json()
    transfer = Transfer(**transfer)
    return transfer


def get_assets(headers: dict) -> List[Asset]:
    response = requests.get(
        f"{base_url()}/assets",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    assets = response.json()
    assets = [Asset(**a) for a in assets]
    return assets


def get_asset_average_load_price(params: dict, headers: dict) -> AverageLoadPrice:
    response = requests.get(
        f"{base_url()}/assets/average-load-price",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    avg_load_price = response.json()
    avg_load_price = AverageLoadPrice(**avg_load_price)
    return avg_load_price


def get_asset_balance(params: dict, headers: dict) -> Balance:
    response = requests.get(
        f"{base_url()}/assets/balance",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    asset_balance = response.json()
    asset_balance = AssetBalance(**asset_balance)
    return asset_balance


def get_asset_allocations(headers: dict) -> List[AssetAllocation]:
    response = requests.get(
        f"{base_url()}/assets/allocations",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    allocations = response.json()
    allocations = [AssetAllocation(**a) for a in allocations]
    return allocations


def get_total_asset_balance(headers: dict) -> Balance:
    response = requests.get(
        f"{base_url()}/assets/total-balance",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    balance = response.json()
    balance = AssetBalance(**balance)
    return balance


def revert_transaction(transaction_id: str, headers: dict) -> Transaction:
    response = requests.post(
        f"{base_url()}/transactions/{transaction_id}/revert",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    transaction = response.json()
    transaction = Transaction(**transaction)
    return transaction


def set_preferred_currency(data: dict, headers: dict) -> UserSettings:
    response = requests.put(
        f"{base_url()}/users/settings",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    user_settings = response.json()
    user_settings = UserSettings(**user_settings)
    return user_settings


def register(data: dict, headers: dict) -> User:
    response = requests.post(
        f"{base_url()}/users",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    user = response.json()
    user = User(**user)
    return user


def create_investment(data: dict, headers: dict) -> Investment:
    response = requests.post(
        f"{base_url()}/investments",
        json=data,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    investment = response.json()
    investment = Investment(**investment)
    return investment


def get_investments(headers: dict) -> List[Investment]:
    response = requests.get(
        f"{base_url()}/investments",
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    investments = response.json()
    investments = [Investment(**i) for i in investments]
    return investments


def get_wallet_history(params: dict, headers: dict) -> List[WalletHistory]:
    response = requests.get(
        f"{base_url()}/wallets-balances/history",
        params=params,
        headers=headers,
    )

    if not response.ok:
        print(response.status_code)
        raise APIError(response.json())

    history = response.json()
    history = [WalletHistory(**h) for h in history]
    return history


def get_asset_history(params: dict, headers: dict) -> List[AssetHistory]:
    response = requests.get(
        f"{base_url()}/assets/history",
        params=params,
        headers=headers,
    )

    if not response.ok:
        print(response.status_code)
        raise APIError(response.json())

    history = response.json()
    history = [AssetHistory(**h) for h in history]
    return history


def get_currency_history(params: dict, headers: dict) -> List[KLines]:
    currency_id = params.pop("currency_id")

    response = requests.get(
        f"{base_url()}/currencies/{currency_id}/klines",
        params=params,
        headers=headers,
    )

    if not response.ok:
        print(response.status_code)
        raise APIError(response.json())

    history = response.json()
    history = [KLines(**h) for h in history]

    return history


def get_capital_gain(params: dict, headers: dict) -> CapitalGain:
    response = requests.get(
        f"{base_url()}/assets/capital-gain",
        params=params,
        headers=headers,
    )

    if not response.ok:
        raise APIError(response.json())

    capital_gain = response.json()
    return CapitalGain(**capital_gain)
