from typing import Callable, Dict
import typing


class BacktestEngineCondition:
    name: str
    params: Dict[str, typing.Any]
    calc: Callable

    def __init__(self, name: str, params: Dict[str, object], calc: Callable):
        self.name = name
        self.params = params
        self.calc = calc