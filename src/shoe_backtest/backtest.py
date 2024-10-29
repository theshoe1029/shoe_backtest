from dataclasses import dataclass
from enum import Enum
from typing import List, Mapping
import numpy as np
import pandas as pd
import numpy.typing as npt


class Side(Enum):
    BUY = 1
    SELL = -1


@dataclass
class Transaction:
    date: pd.Timestamp
    symbol: str
    qty: int
    side: Side


def tx_with_price(tx: Transaction, price: np.float64):
    return {
        "date": tx.date,
        "symbol": tx.symbol,
        "qty": tx.qty,
        "price": price,
        "side": tx.side,
    }


class Portfolio:
    def __init__(self, universe: pd.Series, cash: np.float64):
        self.cash = cash
        self.symbol_to_idx = {}
        for idx, symbol in enumerate(universe):
            self.symbol_to_idx[symbol] = idx
        self.pos = np.zeros(len(self.symbol_to_idx))
        self.avg_cost = np.zeros(len(self.symbol_to_idx))

    def execute(self, tx: Transaction, price: np.float64):
        idx = self.symbol_to_idx[tx.symbol]
        cost = price * tx.qty * tx.side.value
        self.cash -= cost
        pos_new = self.pos[idx] + tx.qty * tx.side.value
        if np.sign(pos_new) == 0:
            self.avg_cost[idx] = 0
        if np.sign(self.pos[idx]) != np.sign(pos_new):
            self.avg_cost[idx] = cost
        else:
            self.avg_cost[idx] = (self.pos[idx] * self.avg_cost[idx] + cost) / pos_new
        self.pos[idx] = pos_new

    def get_pos(self) -> npt.NDArray:
        return np.concat([self.pos, [self.cash]])

    def get_mv(self) -> npt.NDArray:
        return np.multiply(self.pos, self.avg_cost)


class Result:
    def __init__(self):
        self.txns: List[Transaction] = []
        self.positions: List = []
        self.returns: List = []

    def to_df(self, index) -> Mapping[str, pd.DataFrame]:
        return {
            "transactions": pd.DataFrame(self.txns),
            "positions": pd.DataFrame(self.positions, index=index),
            "returns": pd.Series(self.returns, index=index),
        }


def calculate_return(price: pd.Series, price_last: pd.Series, pfv: npt.NDArray):
    if price_last is not None and pfv.sum() > 0:
        w = pfv / pfv.sum()
        r_inst = np.zeros_like(price)
        np.divide(price - price_last, price_last, out=r_inst, where=price_last != 0)
        return np.dot(w, r_inst)
    return 0


def backtest_from_trades(
    txns: Mapping[pd.Timestamp, List[Transaction]],
    price_data: pd.DataFrame,
    cash: np.float64,
) -> Mapping[str, pd.DataFrame]:
    universe = price_data.columns.get_level_values(1).drop_duplicates()
    pf = Portfolio(universe, cash)
    result = Result()
    last_close = None
    for date, row in price_data.iterrows():
        close = row.loc["Close"]
        for tx in txns.get(date, []):
            price = close.loc[tx.symbol]
            pf.execute(tx, price)
            result.txns.append(tx_with_price(tx, price))
        result.positions.append(pf.get_pos())
        result.returns.append(calculate_return(close, last_close, pf.get_mv()))
        last_close = close

    return result.to_df(price_data.index)
