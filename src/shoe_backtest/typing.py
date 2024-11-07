from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd


class Side(Enum):
    BUY = 1
    SELL = -1


@dataclass
class Transaction:
    date: pd.Timestamp
    symbol: str
    qty: np.float64
    side: Side


@dataclass
class PyfolioTransaction:
    date: pd.Timestamp
    symbol: str
    sid: int
    amount: np.float64
    price: np.float64
    txn_dollars: np.float64
