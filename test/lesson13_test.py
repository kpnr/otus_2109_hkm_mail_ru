"""Тесты для урока № 13"""

from typing import Callable
from lesson3.interfaces import GenericCommand
from lesson13.implementations import (
    CommandException, MacroCommand)


class TestCommand(GenericCommand):
    """Тестовая команда"""
    def __init__(self, receiver: Callable):
        super().__init__(receiver)

    def execute(self) -> None:
        self.receiver()


def test_CommandException():
    """Проверим структуру CommandException"""
    try:
        cmd = TestCommand(lambda: None)
        raise CommandException(cmd)
    except CommandException as e:
        assert e.command is cmd and len(e.args) == 1 and e.args[0] is cmd


def test_MacroCommand():
    """Тест макрокоманды"""
    def do(s: str):
        """Модификация target"""
        nonlocal target
        target += s

    target = 'Lesson_'
    cmd1 = TestCommand(lambda: do('1'))
    cmd2 = TestCommand(lambda: do('3'))
    macro = MacroCommand([cmd1, cmd2])
    macro.execute()
    assert target == 'Lesson_13'
