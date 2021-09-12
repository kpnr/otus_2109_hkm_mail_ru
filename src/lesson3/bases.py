"""Базовые классы"""


from __future__ import annotations
from types import SimpleNamespace
from typing import Any, Callable
from abc import ABC, abstractmethod
from .interfaces import GenericInterface
from functools import wraps


class GenericCommand(ABC):
    """Комманда, производящая действия над объектов"""

    def __init__(self, receiver: Any):
        """
        Создание команды
        :param receiver: Объект(-ы) на который действует команда и ее параметры
        :type receiver: instance
        """
        self.receiver = receiver

    @abstractmethod
    def execute(self) -> None:
        """Непосредственное выполнение команды"""


class DynamicInterfaceObject(SimpleNamespace):
    """Объект-свалка для склейки разнородных реализаций интерфейсов"""
    def absorb(self, obj: GenericInterface) -> DynamicInterfaceObject:
        """Поглотить объект - перенести в себя методы и свойства"""
        def to_method(obj: Any, meth: Callable) -> Callable:
            @wraps(meth)
            def f(*args, **kwargs):
                rv = meth(self, *args, **kwargs)
                return rv
            return f
        for k, v in obj.__dict__.items():
            if hasattr(self, k):
                raise AttributeError(f'Attribute {k} already defined',
                                     self, obj)
            setattr(self, k, v)
        for class_obj in obj.__class__.__mro__:
            for k, v in class_obj.__dict__.items():
                if k.startswith('_'):
                    continue
                if hasattr(self, k):
                    continue
                setattr(self, k, to_method(obj,v))
        return self

