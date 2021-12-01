"""Реализция абстракций"""
from typing import MutableSequence, Optional

from lesson3.interfaces import GenericCommand
from .interfaces import CommandQueueInterface, StopCommandLoop, AttractorInterface
from threading import Thread
from queue import Queue


class AttractorStopHardCommand(GenericCommand):
    """Немедленный останов Аттрактора"""
    def __init__(self, receiver: AttractorInterface):
        super().__init__(receiver)

    def execute(self) -> None:
        raise StopCommandLoop('ThreadedAttractor hard stop')


class AttractorStopSoftCommand(GenericCommand):
    """Останов Аттрактора после исчерпания очереди команд"""
    def __init__(self, receiver: AttractorInterface):
        super().__init__(receiver)

    def execute(self) -> None:
        attractor = self.receiver
        queue = attractor.queue_get()
        queue.write(AttractorStopHardCommand(attractor))


class ThreadedQueue(Queue, CommandQueueInterface):
    """Очередь для многопоточного Аттрактора"""
    def read(self) -> GenericCommand:
        """Получение команды"""
        rv = self.get(block=True)
        return rv

    def write(self, command: GenericCommand) -> None:
        """Постановка в очередь"""
        self.put(command, block=True)


class ThreadedAttractor(Thread, AttractorInterface):
    """Интерфейс Аттрактора"""

    def __init__(self):
        self.queue: Optional[CommandQueueInterface] = None
        Thread.__init__(self)

    def start(self, queue: CommandQueueInterface) -> None:
        """Запуск Аттрактора"""
        self.queue = queue
        Thread.start(self)

    def queue_get(self) -> CommandQueueInterface:
        """Получение привязанной очереди команд"""
        rv = self.queue
        return rv

    def command_loop(self) -> None:
        """Цикл выполнения команд"""
        while 1:
            command: GenericCommand = self.queue.read()
            # noinspection PyBroadException
            try:
                command.execute()
            except StopCommandLoop:
                break
            except Exception:
                pass

    def run(self) -> None:
        """Метод, выполняемый в новом потоке"""
        print(f'Attractor {self.name} started')
        self.command_loop()
        return


class ThreadedAttractorStartCommand(GenericCommand):
    """Создание многопоточного аттрактора"""
    def __init__(self, receiver: MutableSequence):
        super().__init__(receiver)

    def execute(self) -> None:
        attractor_list = self.receiver
        queue = ThreadedQueue()
        attractor = ThreadedAttractor()
        attractor.start(queue)
        attractor_list.append(attractor)

