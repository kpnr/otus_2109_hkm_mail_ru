"""Интерфейсы для работы с Аттракторами"""
from abc import abstractmethod
from typing import Optional

from lesson3.interfaces import GenericCommand, GenericInterface


class CommandQueueInterface:
    """Очередь команд Аттрактора"""

    @abstractmethod
    def read(self) -> GenericCommand:
        """Получение команды из очереди с ожиданием"""

    @abstractmethod
    def write(self, command: GenericCommand) -> None:
        """Постановка команды в очередь выполнения"""


class AttractorInterface:
    """Интерфейс Аттрактора"""
    @abstractmethod
    def start(self, queue: CommandQueueInterface) -> None:
        """Привязка очереди команд к Аттрактору"""

    @abstractmethod
    def queue_get(self) -> CommandQueueInterface:
        """Получение очереди команд, к которой привязан Аттрактор"""


class StopCommandLoop(StopIteration):
    """Исключение для остановки аттрактора"""