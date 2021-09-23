"""Интерфейсы объектов игры"""

from __future__ import annotations

from functools import wraps
from types import SimpleNamespace
from typing import Any, Callable, Type
from abc import ABC, abstractmethod


class GenericInterface(ABC):
    """Обобщенный интерфейс"""
    @classmethod
    @abstractmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка, что объект obj поддерживает интерфейс"""

    @staticmethod
    def _not_supported_error(itf_class: Type[GenericInterface], obj: Any):
        """Создание исключения неподдерживаемого интерфейса"""
        raise TypeError('Interface not supported', itf_class, obj)


class SpaceVectorInterface(GenericInterface):
    """Вектор положения/скорости/вращения в пространстве"""
    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка подержки интерфейса"""
        if not (callable(obj.move_by) and callable(obj.rotate)):
            cls._not_supported_error(cls, obj)

    @abstractmethod
    def move_by(self, other: SpaceVectorInterface) -> SpaceVectorInterface:
        """Сложение двух векторов"""

    @abstractmethod
    def rotate(self, rotation: SpaceVectorInterface) -> SpaceVectorInterface:
        """Вращение вектора"""


class PositionedInterface(GenericInterface):
    """Объект, имеющий позицию в пространстве"""
    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка подержки интерфейса"""
        if not callable(obj.position_get):
            cls._not_supported_error(cls, obj)

    @abstractmethod
    def position_get(self) -> SpaceVectorInterface:
        """Получение положения"""


class MovableInterface(PositionedInterface):
    """Объект, допускающий изменние позиции в пространстве"""

    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка подержки интерфейса"""
        super()._assert_support(obj)
        if not callable(obj.position_set):
            cls._not_supported_error(cls, obj)

    @abstractmethod
    def position_set(self, new_pos: SpaceVectorInterface) -> None :
        """Установка положения"""


class SpaceDirectionInterface(GenericInterface):
    """Направление (движения) объекта в пространстве"""
    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка подержки интерфейса"""
        if not (callable(obj.direction_set) or callable(obj.direction_get)):
            cls._not_supported_error(cls, obj)

    @abstractmethod
    def direction_get(self) -> SpaceVectorInterface :
        """Получение направления"""

    @abstractmethod
    def direction_set(self, new_dir: SpaceVectorInterface) -> None :
        """Установка направления"""


class GenericCommand(ABC):
    """Комманда, производящая действия над объектом(-ами)"""

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
        def to_method(meth: Callable) -> Callable:
            """Привязка метода интерфейса с себе. Грязный хак - ломает super()"""
            @wraps(meth)
            def f(*args, **kwargs):
                """Сам перепривязанный метод"""
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
                setattr(self, k, to_method(v))
        return self
