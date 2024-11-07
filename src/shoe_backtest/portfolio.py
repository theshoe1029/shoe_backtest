from typing import List
import warnings
import numpy as np
import numpy.typing as npt

from shoe_backtest.typing import Transaction


class Portfolio:
    def __init__(
        self, idx_to_symbol: List[str], cash: np.float64, commission: np.float64
    ):
        self.cash = cash
        self.commission = commission
        self.v_last = cash
        self.symbol_to_idx = {}
        self.idx_to_symbol = idx_to_symbol
        for idx, symbol in enumerate(idx_to_symbol):
            self.symbol_to_idx[symbol] = idx
        self.pos = np.zeros(len(self.symbol_to_idx))
        self.avg_cost = np.zeros(len(self.symbol_to_idx))

    def execute(self, tx: Transaction, price: np.float64) -> None:
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

    def get_inst_pos(self, symbol: str) -> np.float64:
        return np.float64(self.pos[self.symbol_to_idx[symbol]])

    def get_pos(self) -> npt.NDArray:
        return np.concat([self.pos, [self.cash]])

    def compute_return(self, close: npt.NDArray) -> np.float64:
        v: np.float64 = np.add(np.dot(self.pos, close), self.cash)
        r: np.float64 = np.subtract(np.divide(v, self.v_last), 1)
        self.v_last = v
        return r
