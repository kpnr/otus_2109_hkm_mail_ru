"""Тесты для Состояния"""

import pytest

from queue import Empty, Queue
from threading import Thread
from lesson23.implementations import (
    StatefulAttractor, StopAttractorCommand, NoOpCommand, MoveToCommand,
    RunCommand)
from lesson4.implementations import ThreadedQueue


def test_hard_stop():
    """Завершение Аттрактора по команде StopAttractor"""
    attractor = StatefulAttractor()
    command_queue = ThreadedQueue()
    attractor.start(command_queue)
    stop_command = StopAttractorCommand(attractor)
    command_queue.write(stop_command)
    attractor.join(1.0)


def test_move_to_command():
    """Проверка состояния MoveTo и переключние обратно в Run"""
    attractor = StatefulAttractor()
    assert isinstance(attractor, Thread)
    command_queue = ThreadedQueue()
    assert isinstance(command_queue, Queue)
    command_queue_2 = ThreadedQueue()
    attractor.start(command_queue)
    move_to_command = MoveToCommand((attractor, command_queue_2))
    command_queue.write(move_to_command)
    noop_command = NoOpCommand(None)
    command_queue.write(noop_command)

    # проверим, что noop_command была ретранслирована во вторую очередь
    assert command_queue_2.get(True, 1.0) is noop_command

    # переключение в режим Run
    run_command = RunCommand(attractor)
    command_queue.write(run_command)
    assert command_queue_2.get(True, 1.0) is run_command
    run_command.execute()

    # эта команда должна выполниться в аттракторе
    noop_command = NoOpCommand(None)
    command_queue.write(noop_command)
    # соответственно, не должна дойти до второй очереди команд
    with pytest.raises(Empty):
        command_queue_2.get(True, 1.0)

    # теперь надо завершить аттрактор, иначе тест не считается завершенным
    stop_command = StopAttractorCommand(attractor)
    command_queue.write(stop_command)
    attractor.join(1.0)

