"""Реализция абстракций"""
from lesson3.interfaces import GenericCommand, abstractmethod
from typing import Optional
from contextlib import suppress

class CommandQueue:
    @abstractmethod
    def read(self, lock=True) -> Optional[GenericCommand]:
        """Получение команды из очереди (возможно, с ожиданием)"""
    @abstractmethod
    def write(self, command: GenericCommand) -> None:
        """Постановка команды в очередь выполнения"""

class Attractor:
    def __init__(self, command_queue: CommandQueue):
        self.command_queue = command_queue
        self.is_terminated = False

    def command_loop(self):
        """Цикл выполнения команд"""
        while not self.is_terminated:
            command: GenericCommand = self.command_queue.read()
            with suppress(Exception):
                command.execute()

    