import logging
from typing import Type, TypeVar, Optional

T = TypeVar('T')

class ProxyLocatorCS:
    # Private class-level dictionary
    _locator = {}
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProxyLocatorCS, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, interface, proxy):
        if interface not in cls._locator:
            logging.info(f"Registering {interface} with {proxy}")
            cls._locator[interface] = proxy

    @classmethod
    def get_by_interface(cls, interface: Type[T]) -> T:
        if interface not in cls._locator:
            logging.warning(f"{interface} not found in locator.")
            raise ValueError(f"{interface} not found in locator.")
        
        return cls._locator[interface]
