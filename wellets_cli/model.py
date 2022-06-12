from datetime import datetime
from typing import List

from pydantic import BaseModel


class UserCurrency(BaseModel):
    id: str
    acronym: str
    alias: str
    dollar_rate: float
    created_at: datetime
    updated_at: datetime
    favorite: bool


class Wallet(BaseModel):
    id: str
    alias: str
    balance: float
    currency_id: str
    created_at: datetime
    updated_at: datetime
    portfolios: List[str] = None


class Currency(BaseModel):
    id: str
    acronym: str
    alias: str
    dollar_rate: float
    created_at: datetime
    updated_at: datetime


class UserSettings(BaseModel):
    id: str
    user_id: str
    currency_id: str
    created_at: str
    updated_at: str
    currency: Currency


class WalletAverageLoadPrice(BaseModel):
    average_load_price: float = None
    base_currency: Currency


class Balance(BaseModel):
    balance: float
    currency: Currency


class Portfolio(BaseModel):
    id: str
    alias: str
    weight: float
    created_at: datetime
    updated_at: datetime
    user_id: str
    parent_id: str = None
    parent: "Portfolio" = None
    children: List["Portfolio"] = []


class RebalanceAction(BaseModel):
    type: str
    amount: float

class RebalanceChange(BaseModel):
    portfolio: Portfolio
    wallets: List[Wallet]
    target: float
    actual: float
    weight: float
    off_by: float
    action: RebalanceAction


class PortfolioRebalance(BaseModel):
    changes: List[RebalanceChange]
    currency: Currency
