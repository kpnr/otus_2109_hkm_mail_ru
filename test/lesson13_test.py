"""Тесты для урока № 13"""

from typing import Callable, cast
from pytest import raises, approx
from lesson3.interfaces import GenericCommand
from lesson3.implementations import Tank, Movable, SpaceDirection
from lesson13.interfaces import FuelInterface
from lesson13.implementations import (
    CommandException, MacroCommand, CheckFuelCommand, BurnFuelCommand,
    LinearVector2, StraightMoveWithFuelCommand)


class CallbackCommand(GenericCommand):
    """Тестовая команда-callback"""
    def __init__(self, receiver: Callable):
        super().__init__(receiver)

    def execute(self) -> None:
        """Выполнить обратный вызов"""
        self.receiver()


def test_CommandException():
    """Проверим структуру CommandException"""
    cmd = CallbackCommand(lambda: None)
    try:
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
    cmd1 = CallbackCommand(lambda: do('1'))
    cmd2 = CallbackCommand(lambda: do('3'))
    macro = MacroCommand([cmd1, cmd2])
    macro.execute()
    assert target == 'Lesson_13'


# noinspection PyMissingOrEmptyDocstring
class Vehicle(FuelInterface):
    """Тестовая "машинка" для проверки уровня топлива"""

    def __init__(self):
        self.fuel_quantity = 10.0
        self.fuel_rate = 2.0

    def fuel_quantity_get(self) -> float:
        return self.fuel_quantity

    def fuel_quantity_set(self, quantity: float) -> None:
        self.fuel_quantity = quantity

    def fuel_rate_get(self) -> float:
        return self.fuel_rate

    def fuel_rate_set(self, rate: float) -> None:
        self.fuel_rate = rate


def test_CheckFuelCommand_ok():
    """Тест выполнения для достаточного уровня топлива"""
    movement = LinearVector2(3.0, 4.0)  # Перемещение ровно на 5 единиц
    vehicle = Tank()
    vehicle.absorb(Vehicle())
    cmd = CheckFuelCommand((cast(FuelInterface, vehicle), movement))
    cmd.execute()


def test_CheckFuelCommand_fail():
    """Тест выполнения для недостаточного уровня топлива"""
    movement = LinearVector2(3.01, 4.0)  # Перемещение более 5 единиц
    vehicle = Tank()
    vehicle.absorb(Vehicle())
    cmd = CheckFuelCommand((cast(FuelInterface, vehicle), movement))
    with raises(CommandException):
        cmd.execute()


def test_BurnFuelCommand():
    """Тест на расход топлива"""
    movement = LinearVector2(3.0, 4.0)  # Перемещение 5 единиц
    vehicle = Tank()
    vehicle.absorb(Vehicle())
    cmd = BurnFuelCommand((cast(FuelInterface, vehicle), movement))
    cmd.execute()
    assert cast(FuelInterface, vehicle).fuel_quantity_get() == approx(0.0)


def test_StraitMoveWithFuelCommand():
    """Тест перемещения с топливом"""
    vehicle = Tank()
    vehicle.absorb(Vehicle())
    position = LinearVector2(1.0, 1.0)
    vehicle.absorb(Movable(position))
    speed = LinearVector2(3.0, 4.0)
    vehicle.absorb(SpaceDirection(speed))
    cmd = StraightMoveWithFuelCommand(vehicle)
    cmd.execute()
    position = vehicle.position_get()
    # доехали до точки
    assert position.x == approx(4.0) and position.y == approx(5.0)
    # и сожгли топливо
    assert vehicle.fuel_quantity_get() == approx(0.0)
