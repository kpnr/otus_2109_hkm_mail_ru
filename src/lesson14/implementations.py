"""Реализация IOC"""
from typing import Any, Callable
from threading import RLock, local
from .interfaces import IoCController


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


class ThreadSafeIoC(SimpleIoC):
    """Потокобезопасный (с межпоточной блокировкой)"""
    def __init__(self):
        super().__init__()
        self.locker = RLock()

    def resolve(self, key: str, *args, **kwargs) -> Any:
        """Потокобезопасное разрешение зависимостей"""
        with self.locker:
            rv = super().resolve(key, *args, **kwargs)
        return rv


class ThreadLocalIoC(IoCController):
    """
    С разделением по потокам - каждый поток имеет свои зависимости,
    т.е. ключом служит пара (Поток, Имя_Зависимости)
    """

    def __init__(self):
        self.symbols = local()

    def _register(self, key: str, value: Callable) -> Any:
        self.symbols.__dict__[key] = value

    def resolve(self, key: str, *args, **kwargs) -> Any:
        """Локальный для потока IoC"""
        # В новом потоке список зависимостей пуст, поэтому нужно зарегистрировать регистратора
        self.symbols.__dict__.setdefault('ioc.register', self._register)
        rv = self.symbols.__dict__[key](*args, **kwargs)
        return rv
