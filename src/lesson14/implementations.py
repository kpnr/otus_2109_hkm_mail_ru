"""Реализация IOC"""
from typing import Any, Callable
from .interfaces import IoCController


# class DeferCallCommand(GenericCommand):
#     """Превращаем произвольный вызов в команду"""
#
#     def __init__(self, receiver:Tuple(Callable, List, Dict)):

class SimpleIoC(IoCController):
    """
    Простейшая реализация на основе словаря.

    Создается с единственной командой ioc.register(key, value)
    """

    def __init__(self):
        self.symbols = {'ioc.register': self._register}

    def _register(self, key: str, value: Callable) -> Any:
        self.symbols[key] = value

    def resolve(self, key: str, *args, **kwargs) -> Any:
        """Разрешение символа и его выполнение"""
        rv = self.symbols[key](*args, **kwargs)
        return rv


class PolymorphIoC(IoCController):
    """
    Контроллер, позволяющий изменять реализации "на лету"
    командой ioc.replace(new_ioc).

    По-умолчанию инициализируется с SimpleIoC
    """
    ioc: IoCController

    def __init__(self):
        self._replace(SimpleIoC())

    def _replace(self, new_ioc: IoCController):
        new_ioc.resolve('ioc.register', 'ioc.replace', lambda new_ioc: self._replace(new_ioc))
        self.ioc = new_ioc

    def resolve(self, key: str, *args, **kwargs) -> Any:
        """Разрешение символа через внешний IoC"""
        rv = self.ioc.resolve(key, *args, **kwargs)
        return rv
