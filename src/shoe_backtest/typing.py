from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Side(Enum):
    BUY = 1
    SELL = -1


@dataclass
class Transaction:
    date: pd.Timestamp
    symbol: str
    qty: float
    side: Side


@dataclass
class PyfolioTransaction:
    date: pd.Timestamp
    symbol: str
    sid: int
    amount: float
    price: float
    txn_dollars: float
