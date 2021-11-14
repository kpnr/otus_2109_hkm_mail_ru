"""Интерфейсы/абстракции"""
from typing import Any
from abc import abstractmethod
from lesson3.interfaces import (
    GenericInterface, SpaceVectorInterface)


class MetricVectorInterface(SpaceVectorInterface):
    """Вектор метрикой-длиной"""
    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        if not (callable(obj.length)):
            cls._not_supported_error(cls, obj)
        super(MetricVectorInterface, cls)._assert_support(obj)

    @abstractmethod
    def length(self) -> float:
        """Получить длину вектора"""


class FuelInterface(GenericInterface):
    """Работа с топливом"""

    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        """Проверка подержки интерфейса"""
        for attr_name in {'fuel_quantity_get', 'fuel_quantity_set',
                          'fuel_rate_get', 'fuel_rate_set'}:
            if not callable(getattr(obj, attr_name)):
                cls._not_supported_error(cls, obj)

    @abstractmethod
    def fuel_quantity_get(self) -> float:
        """Получить уровень топлива"""

    @abstractmethod
    def fuel_quantity_set(self, quantity: float) -> None:
        """Установить уровень топлива"""

    @abstractmethod
    def fuel_rate_get(self) -> float:
        """Получить номинальный расход топлива"""

    @abstractmethod
    def fuel_rate_set(self, rate: float) -> float:
        """Установить номинальный расход топлива"""
