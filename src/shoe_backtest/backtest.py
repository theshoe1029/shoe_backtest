from typing import Callable, List, Mapping, Tuple
import pandas as pd
import numpy as np
import numpy.typing as npt

from shoe_backtest.portfolio import Portfolio
from shoe_backtest.result import Result
from shoe_backtest.typing import Side, Transaction


def backtest_from_strategy(
    price_data: pd.DataFrame,
    cash: np.float64,
    commission: np.float64,
    strategy: Callable[[str, npt.NDArray, Portfolio, Tuple], List[Transaction]],
    *strategy_args: Tuple,
) -> List[pd.DataFrame]:
    def supply_txns(
        date: str, historic_data: npt.NDArray, pf: Portfolio
    ) -> List[Transaction]:
        txns = strategy(date, historic_data, pf, strategy_args)
        if txns is None:
            raise Exception("A strategy must return a list on each date")
        return txns

    return __backtest(supply_txns, price_data, cash, commission)


def backtest_from_trades(
    txns: Mapping[str, List[Transaction]],
    price_data: pd.DataFrame,
    cash: np.float64,
    commission: np.float64,
) -> List[pd.DataFrame]:
    def supply_txns(
        date: str, historic_data: npt.NDArray, pf: Portfolio
    ) -> List[Transaction]:
        return txns.get(date, [])

    return __backtest(supply_txns, price_data, cash, commission)


def backtest_from_positions(
    history: Mapping[str, Mapping[str, np.float64]],
    price_data: pd.DataFrame,
    cash: np.float64,
    commission: np.float64,
) -> List[pd.DataFrame]:
    def supply_txns(
        date: str, historic_data: npt.NDArray, pf: Portfolio
    ) -> List[Transaction]:
        return __txns_from_pos(date, pf, history.get(date, {}))

    return __backtest(supply_txns, price_data, cash, commission)


def __backtest(
    supply_txns: Callable[[str, npt.NDArray, Portfolio], List[Transaction]],
    price_data: pd.DataFrame,
    cash: np.float64,
    commission: np.float64,
) -> List[pd.DataFrame]:
    universe = __price_data_to_instruments(price_data)
    pf = Portfolio(universe, cash, commission)
    result = Result(price_data.index)
    close_data: npt.NDArray = price_data["Close"].to_numpy()
    for i, close in enumerate(close_data):
        date = price_data.index[i]
        txns = supply_txns(date, close_data[:i], pf)
        result.update(close, txns, pf)
    return result.to_df()


def __txns_from_pos(
    date: str, pf: Portfolio, pos: Mapping[str, np.float64]
) -> List[Transaction]:
    txns = []
    for inst, qty in pos.items():
        tx_qty = qty - pf.get_inst_pos(inst)
        tx_side = Side.SELL if tx_qty < 0 else Side.BUY
        tx = Transaction(
            date=date,
            symbol=inst,
            qty=tx_qty,
            side=tx_side,
        )
        txns.append(tx)
    return txns


def __price_data_to_instruments(price_data: pd.DataFrame) -> List[str]:
    instruments: List[str] = (
        price_data.columns.get_level_values(1).drop_duplicates().to_list()
    )
    return instruments
