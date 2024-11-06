from typing import Callable, List, Mapping, Tuple
import pandas as pd

from shoe_backtest.portfolio import Portfolio
from shoe_backtest.result import Result
from shoe_backtest.typing import Side, Transaction


def backtest_from_strategy(
    price_data: pd.DataFrame,
    cash: float,
    commission: float,
    strategy: Callable[[str, Portfolio, Tuple], List[Transaction]],
    *strategy_args: Tuple,
) -> List[pd.DataFrame]:
    def supply_txns(date: str, pf: Portfolio) -> List[Transaction]:
        txns = strategy(date, pf, strategy_args)
        if txns is None:
            raise Exception("A strategy must return a list on each date")
        return txns

    return __backtest(supply_txns, price_data, cash, commission)


def backtest_from_trades(
    txns: Mapping[str, List[Transaction]],
    price_data: pd.DataFrame,
    cash: float,
    commission: float,
) -> List[pd.DataFrame]:
    def supply_txns(date: str, _: Portfolio) -> List[Transaction]:
        return txns.get(date, [])

    return __backtest(supply_txns, price_data, cash, commission)


def backtest_from_positions(
    history: Mapping[str, Mapping[str, float]],
    price_data: pd.DataFrame,
    cash: float,
    commission: float,
) -> List[pd.DataFrame]:
    def supply_txns(date: str, pf: Portfolio) -> List[Transaction]:
        return __txns_from_pos(date, pf, history.get(date, {}))

    return __backtest(supply_txns, price_data, cash, commission)


def __backtest(
    supply_txns: Callable[[str, Portfolio], List[Transaction]],
    price_data: pd.DataFrame,
    cash: float,
    commission: float,
) -> List[pd.DataFrame]:
    universe = __price_data_to_instruments(price_data)
    pf = Portfolio(universe, cash, commission)
    result = Result(price_data.index)
    for date, row in price_data.iterrows():
        close = row.loc["Close"]
        txns = supply_txns(date, pf)
        result.update(close, txns, pf)
    return result.to_df()


def __txns_from_pos(
    date: str, pf: Portfolio, pos: Mapping[str, float]
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


def __price_data_to_instruments(price_data: pd.DataFrame) -> pd.Index:
    return price_data.columns.get_level_values(1).drop_duplicates()
