"""Интерфейсы IOC"""
from __future__ import annotations
from typing import Any
from lesson3.interfaces import GenericInterface

from abc import abstractmethod


class IoCController(GenericInterface):
    """Интерфейс IOC"""

    @classmethod
    def _assert_support(cls, obj: Any) -> None:
        if not (callable(obj.resolve)):
            cls._not_supported_error(cls, obj)

    @abstractmethod
    def resolve(self, key: str, *args, **kwargs) -> Any:
        """Получить объект по ключу"""
