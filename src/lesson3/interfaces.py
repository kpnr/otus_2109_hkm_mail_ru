"""Интерфейсы объектов игры"""

from __future__ import annotations
from typing import Any, Type
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
