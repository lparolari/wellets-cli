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
