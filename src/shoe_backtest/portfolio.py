import warnings
import numpy as np
import pandas as pd
import numpy.typing as npt

from shoe_backtest.typing import Transaction


class Portfolio:
    def __init__(self, instruments: pd.Series, cash: float, commission: float):
        self.cash = cash
        self.commission = commission
        self.v_last = cash
        self.symbol_to_idx = {}
        for idx, symbol in enumerate(instruments):
            self.symbol_to_idx[symbol] = idx
        self.pos = np.zeros(len(self.symbol_to_idx))
        self.avg_cost = np.zeros(len(self.symbol_to_idx))

    def execute(self, tx: Transaction, price: float) -> None:
        idx = self.symbol_to_idx[tx.symbol]
        cost = price * tx.qty * tx.side.value
        fee_rate = 1 + tx.side.value * (self.commission / 10000)
        self.cash -= cost * fee_rate
        if self.cash < 0:
            warnings.warn(
                f"Transaction {tx} has caused the portfolio cash to drop to ${self.cash}"
            )
        pos_new = self.pos[idx] + tx.qty * tx.side.value
        if np.sign(pos_new) == 0:
            self.avg_cost[idx] = 0
        if np.sign(self.pos[idx]) != np.sign(pos_new):
            self.avg_cost[idx] = cost
        else:
            self.avg_cost[idx] = (self.pos[idx] * self.avg_cost[idx] + cost) / pos_new
        self.pos[idx] = pos_new

    def get_inst_pos(self, symbol: str) -> float:
        return float(self.pos[self.symbol_to_idx[symbol]])

    def get_pos(self) -> npt.NDArray:
        return np.concat([self.pos, [self.cash]])

    def compute_return(self, close: pd.Series) -> float:
        v: float = np.dot(self.pos, close) + self.cash
        r = v / self.v_last - 1
        self.v_last = v
        return r
