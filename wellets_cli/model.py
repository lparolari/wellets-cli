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


class Currency(BaseModel):
    id: str
    acronym: str
    alias: str
    dollar_rate: float
    created_at: datetime
    updated_at: datetime


class Wallet(BaseModel):
    id: str
    alias: str
    balance: float
    currency_id: str
    created_at: datetime
    updated_at: datetime
    portfolios: List[str] = None
    currency: Currency = None

    def __eq__(self, other: "Wallet"):
        return self.id == other.id


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
    wallets: List[Wallet] = []

    def __eq__(self, other: "Portfolio"):
        return self.id == other.id


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


class Transaction(BaseModel):
    id: str
    value: float
    description: str
    dollar_rate: float
    wallet_id: str
    created_at: datetime
    updated_at: datetime
    wallet: Wallet


class Duration(BaseModel):
    years: int = None
    months: int = None
    weeks: int = None
    days: int = None
    hours: int = None
    minutes: int = None
    seconds: int = None


class AccumulationEntry(BaseModel):
    id: str
    value: float
    description: str
    dollar_rate: float
    wallet_id: str
    created_at: datetime
    updated_at: datetime


class Accumulation(BaseModel):
    id: str
    alias: str
    strategy: str
    quote: float
    planned_entries: int
    every: Duration
    planned_start: datetime
    planned_end: datetime
    created_at: datetime
    updated_at: datetime
    wallet_id: str
    entries: List[AccumulationEntry]


class NextAccumulationEntry(BaseModel):
    entry: int
    amount: float
    current: float
    target: float
    date: datetime
