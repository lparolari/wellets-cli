from datetime import datetime
from typing import List

from pydantic import BaseModel


class Currency(BaseModel):
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


class PlainCurrency(BaseModel):
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
    currency: PlainCurrency


class WalletAverageLoadPrice(BaseModel):
    average_load_price: float = None
    base_currency: PlainCurrency
