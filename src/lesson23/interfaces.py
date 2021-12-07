"""Интерфейсы для Аттрактора с Состоянием"""

from lesson4.interfaces import (
    AttractorInterface, abstractmethod, GenericCommand)


class AttractorStateInterface:
    """Состояние Аттрактора"""

    @abstractmethod
    def execute(self, command: GenericCommand) -> None:
        """Выполнить команду"""


class StatefulAttractorInterface(AttractorInterface):
    """Интерфейс аттрактора с состоянием"""

    @abstractmethod
    def state_set(self, new_state: AttractorStateInterface) -> None:
        """Установить состояние"""
        self.state = new_state

    @abstractmethod
    def state_get(self) -> AttractorStateInterface:
        """Получить состояние"""
        return self.state
