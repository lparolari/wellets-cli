from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class Currency(BaseModel):
    id: str
    acronym: str
    alias: str
    dollar_rate: float
    created_at: datetime
    updated_at: datetime


class UserCurrency(Currency):
    favorite: bool


class Wallet(BaseModel):
    id: str
    alias: str
    description: Optional[str] = None
    balance: float
    currency_id: str
    created_at: datetime
    updated_at: datetime
    portfolios: Optional[List[str]] = None
    currency: Optional[Currency] = None

    def __eq__(self, other: object):
        if not isinstance(other, Wallet):
            return False
        return self.id == other.id


class UserSettings(BaseModel):
    id: str
    user_id: str
    currency_id: str
    created_at: str
    updated_at: str
    currency: Currency


class User(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime


class WalletAverageLoadPrice(BaseModel):
    average_load_price: Optional[float] = None
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
    parent_id: Optional[str] = None
    parent: Optional["Portfolio"] = None
    children: List["Portfolio"] = []
    wallets: List[Wallet] = []

    def __eq__(self, other: object):
        if not isinstance(other, Portfolio):
            return False
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
    wallet_id: str
    created_at: datetime
    updated_at: datetime
    wallet: Wallet


class Duration(BaseModel):
    years: Optional[int] = None
    months: Optional[int] = None
    weeks: Optional[int] = None
    days: Optional[int] = None
    hours: Optional[int] = None
    minutes: Optional[int] = None
    seconds: Optional[int] = None


class AccumulationEntry(BaseModel):
    id: str
    value: float
    description: str
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
    asset_id: str
    entries: List[AccumulationEntry]


class NextAccumulationEntry(BaseModel):
    entry: int
    amount: float
    current: float
    target: float
    date: datetime


class Transfer(BaseModel):
    id: str


class AssetEntry(BaseModel):
    id: str
    value: float
    dollar_rate: float
    asset_id: str
    created_at: datetime
    updated_at: datetime


class Asset(BaseModel):
    id: str
    balance: float
    entries: List[AssetEntry]
    user_id: str
    currency_id: str
    created_at: datetime
    updated_at: datetime
    currency: Currency


class AverageLoadPrice(BaseModel):
    average_load_price: Optional[float] = None


class AssetBalance(BaseModel):
    balance: float


class AssetAllocation(BaseModel):
    balance: float
    allocation: float
    asset: Asset


class Investment(BaseModel):
    CREATED: str = "created"
    STARTED: str = "started"
    CLOSED: str = "closed"

    id: str
    alias: str
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    entries: Any = []

    def is_active(self):
        return self.status == self.STARTED

    def is_created(self):
        return self.status == self.CREATED

    def is_closed(self):
        return self.status == self.CLOSED


class WalletHistory(BaseModel):
    timestamp: datetime
    balance: float


class AssetHistory(BaseModel):
    timestamp: datetime
    balance: float


class KLines(BaseModel):
    open_time: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float


class CapitalGain(BaseModel):
    current_price: float
    basis_price: float
    gain_amount: float
    gain_rate: float
