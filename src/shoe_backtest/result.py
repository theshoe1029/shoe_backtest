from typing import List
import pandas as pd

from shoe_backtest.portfolio import Portfolio
from shoe_backtest.typing import PyfolioTransaction, Transaction


class Result:
    def __init__(self, idx: pd.Index):
        self.idx = idx
        self.txns: List[PyfolioTransaction] = []
        self.positions: List = []
        self.returns: List = []

    def update(
        self,
        close: pd.Series,
        txns: List[Transaction],
        pf: Portfolio,
    ) -> None:
        self.returns.append(pf.compute_return(close))
        for tx in txns:
            price = close.loc[tx.symbol]
            pf.execute(tx, price)
            self.txns.append(
                PyfolioTransaction(
                    date=tx.date,
                    symbol=tx.symbol,
                    sid=pf.symbol_to_idx[tx.symbol],
                    amount=tx.qty * tx.side.value,
                    price=price,
                    txn_dollars=-1 * tx.qty * tx.side.value * price,
                )
            )
        self.positions.append(pf.get_pos())

    def to_df(self) -> List[pd.DataFrame]:
        txns_df = pd.DataFrame()
        if len(self.txns) > 0:
            txns_df = pd.DataFrame(self.txns)
            txns_df.index = pd.to_datetime(txns_df["date"])
            txns_df = txns_df[["amount", "price", "sid", "symbol", "txn_dollars"]]
        pos_df = pd.DataFrame(self.positions, index=pd.to_datetime(self.idx))
        pos_df = pos_df.rename(columns={pos_df.columns[-1]: "cash"})
        return [
            txns_df,
            pos_df,
            pd.Series(self.returns, index=pd.to_datetime(self.idx)),
        ]
