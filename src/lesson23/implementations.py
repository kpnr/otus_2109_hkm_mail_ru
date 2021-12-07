"""Реализация Аттракторов с Состоянием и команд для них"""

from typing import Any, cast, Tuple
from .interfaces import (
    GenericCommand, AttractorStateInterface, StatefulAttractorInterface)
from lesson4.interfaces import (
    CommandQueueInterface, StopCommandLoop)
from lesson4.implementations import ThreadedAttractor
from lesson13.implementations import MacroCommand


class RunningState(AttractorStateInterface):
    """Обычное выполнение команд"""

    def execute(self, command: GenericCommand) -> None:
        """простое выполнение команды"""
        command.execute()


class MoveToState(AttractorStateInterface):
    """Переброс команды из одной очереди в другую"""

    def __init__(self, target_queue: CommandQueueInterface):
        self.target_queue = target_queue

    def execute(self, command: GenericCommand) -> None:
        """Перебрасываем команды другому Аттрактору"""
        self.target_queue.write(command)


class StopState(AttractorStateInterface):
    """Остановленный Аттрактор"""
    def execute(self, command: GenericCommand) -> None:
        """На любую команду кидаем исключение"""
        raise StopCommandLoop('Состояние останова')


class AttractorStateModifyCommand(GenericCommand):
    """Базовая команда по изменению состояния аттрактора"""

    def __init__(self, receiver: Any):
        """receiver - кортеж (ЦелевойАттрактор, ЦелевоеСостояние)"""
        attractor, state = receiver
        if not isinstance(attractor, StatefulAttractorInterface):
            raise ValueError('AttractorStateModifyCommand. '
                             'Требуется StatefulAttractorInterface')
        if not isinstance(state, AttractorStateInterface):
            raise ValueError('AttractorStateModifyCommand.'
                             'Требуется AttractorStateInterface')
        super(GenericCommand, self).__init__(receiver)

    def execute(self) -> None:
        """Заменяем состояние у цели"""
        attractor, state = cast(
                Tuple[StatefulAttractorInterface, AttractorStateInterface],
                self.receiver)
        attractor.state_set(state)


class StopAttractorCommand(MacroCommand):
    """Команда жесткой остановки"""

    def __init__(self, receiver: Any):
        """receiver - Целевой Аттрактор"""
        attractor = receiver
        if not isinstance(attractor, StatefulAttractorInterface):
            raise ValueError('StopAttractorCommand.'
                             'Требуется StatefulAttractorInterface')
        state = StopState()
        state_set_command = AttractorStateModifyCommand((state, attractor))
        finalize_command = ???
        super(AttractorStateModifyCommand, self).__init__()


class MoveToCommand(AttractorStateModifyCommand):
    """Команда на включение режимма "перекачки" """
    def __init__(self, receiver: Any):
        """receiver - кортеж (ЦелевойАттрактор, ЦелеваяОчередь)"""
        attractor, queue = receiver
        if not isinstance(attractor, StatefulAttractorInterface):
            raise ValueError('MoveToCommand.'
                             'Требуется StatefulAttractorInterface')
        if not isinstance(queue, CommandQueueInterface):
            raise ValueError('MoveToCommand.'
                             'Требуется CommandQueueInterface')
        state = MoveToState(queue)
        super(AttractorStateModifyCommand, self).__init__((attractor, state))


class RunCommand(AttractorStateModifyCommand):
    """Команда на включение обычного режимма"""

    def __init__(self, receiver: Any):
        """receiver - Целевой Аттрактор"""
        attractor = receiver
        if not isinstance(attractor, StatefulAttractorInterface):
            raise ValueError('RunCommand.'
                             'Требуется StatefulAttractorInterface')
        state = RunningState()
        super(AttractorStateModifyCommand, self).__init__((attractor, state))


class StatefulAttractor(ThreadedAttractor, StatefulAttractorInterface):
    """Многопоточный Аттрактор с состоянием (стратегией) обработки команд"""

    def __init__(self):
        super(ThreadedAttractor, self).__init__()
        self.state = RunningState()


    def state_set(self, new_state: AttractorStateInterface) -> None:
        """Запись состояния"""
        self.state = new_state

    def state_get(self) -> AttractorStateInterface:
        """Получение состояния"""
        return self.state

    def command_loop(self) -> None:
        """Цикл обработки команд. Совпадает с обычным многопоточным аттрактором
        за исключением:
        (1)выполнение команды делегировано Состоянию
        """
        while 1:
            command: GenericCommand = self.queue.read()
            # noinspection PyBroadException
            try:
                self.state_get().execute(command)
            except StopCommandLoop:
                break
            except Exception:
                pass
        return