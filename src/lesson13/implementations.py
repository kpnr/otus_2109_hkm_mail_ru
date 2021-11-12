"""Реализации интерфейсов/абстракций"""

from typing import Any, Optional, cast

from lesson3.interfaces import GenericCommand


class CommandException(Exception):
    """Исключение выполнения команды"""
    def __init__(self, cmd: Optional[GenericCommand]):
        self.command = cmd
        super(CommandException, self).__init__(cmd)


# noinspection PyMissingOrEmptyDocstring
class MacroCommand(GenericCommand):
    """Макрокоманда - последовательное выполнение нескольких команд"""

    def __init__(self, receiver: Any):
        """receiver - последовательность команд для выполнения"""
        super().__init__(receiver)

    def execute(self) -> None:
        x = None
        try:
            for x in self.receiver:
                cast(GenericCommand, x).execute()
        except Exception as e:
            raise CommandException(x) from e

