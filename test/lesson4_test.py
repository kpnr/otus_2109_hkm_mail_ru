"""Тесты для урока № 4"""

from lesson3.interfaces import GenericCommand
from lesson4.implemetations import (ThreadedAttractorStartCommand,
                                    AttractorStopHardCommand,
                                    AttractorStopSoftCommand,
                                    ThreadedAttractor,
                                    ThreadedQueue)
from threading import Thread
from queue import Queue


class ExceptionCommand(GenericCommand):
    """Тестовая команда-исключение"""
    def __init__(self, receiver: str):
        super().__init__(receiver)

    def execute(self) -> None:
        raise Exception(self.receiver)


def test_start_command():
    attractor_list = []
    cmd = ThreadedAttractorStartCommand(attractor_list)
    assert len(attractor_list) == 0
    cmd.execute()
    assert len(attractor_list) == 1
    attractor: ThreadedAttractor = attractor_list[0]
    cmd = AttractorStopHardCommand(attractor)
    queue = attractor.queue_get()
    assert isinstance(attractor, Thread)
    assert attractor.is_alive()
    queue.write(cmd)
    attractor.join(10.0)
    assert not attractor.is_alive()


def test_hard_stop():
    attractor = ThreadedAttractor()
    queue = ThreadedQueue()
    cmd = AttractorStopHardCommand(attractor)
    queue.write(cmd)
    cmd = ExceptionCommand('test')
    queue.write(cmd)
    attractor.start(queue)
    assert isinstance(attractor, Thread)
    attractor.join()
    assert isinstance(queue, Queue)
    assert not queue.empty()


def test_soft_stop():
    attractor = ThreadedAttractor()
    queue = ThreadedQueue()
    cmd = AttractorStopSoftCommand(attractor)
    queue.write(cmd)
    cmd = ExceptionCommand('test')
    queue.write(cmd)
    attractor.start(queue)
    assert isinstance(attractor, Thread)
    attractor.join()
    assert isinstance(queue, Queue)
    assert queue.empty()

