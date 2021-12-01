"""Реализации интерфейсов/абстракций"""
from abc import ABC
from typing import Any, Optional, Tuple, cast

from lesson13.interfaces import FuelInterface, MetricVectorInterface
from lesson3.interfaces import GenericCommand
from lesson3.implementations import SpaceVector2, StraightMoveCommand


class CommandException(Exception):
    """Исключение выполнения команды"""
    def __init__(self, cmd: Optional[GenericCommand]):
        self.command = cmd
        super(CommandException, self).__init__(cmd)


class FuelException(CommandException):
    """Исключение контроля/сжигания топлива"""
    def __init__(self, cmd: GenericCommand,
                 fuel_actual: float, fuel_required: float):
        self.fuel_actual, self.fuel_required = fuel_actual, fuel_required
        super().__init__(cmd)


class LinearVector2(SpaceVector2, MetricVectorInterface):
    """Евклидов вектор в 2D"""

    def length(self) -> float:
        """Обычная длина (по Пифагору)"""
        rv = (self.x ** 2 + self.y ** 2) ** (1/2)
        return rv


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


class FuelCommand(GenericCommand, ABC):
    """Базовый класс для проверки и сжигания топлива"""
    def __init__(self, receiver: Tuple[FuelInterface, MetricVectorInterface]):
        vehicle, movement = receiver
        FuelInterface._assert_support(vehicle)
        MetricVectorInterface._assert_support(movement)
        super().__init__((vehicle, movement))

    def _fuel_expense_get(self) -> float:
        """Получить фактический расход топлива"""
        vehicle, movement = self.receiver
        length = cast(MetricVectorInterface, movement).length()
        fuel_rate = cast(FuelInterface, vehicle).fuel_rate_get()
        rv = fuel_rate * length
        return rv


class CheckFuelCommand(FuelCommand):
    """Проверить кол-во топлива, достаточное для движения"""

    def execute(self) -> None:
        """Контроль досаточности топлива"""
        vehicle, _ = self.receiver
        fuel_quantity = cast(FuelInterface, vehicle).fuel_quantity_get()
        fuel_required = self._fuel_expense_get()
        if fuel_quantity < fuel_required:
            raise FuelException(self, fuel_quantity, fuel_required)
        # Проверка уровня топлива прошла


class BurnFuelCommand(FuelCommand):
    """Израсходовать топливо"""

    def execute(self) -> None:
        """Уничтожение топлива для перехода"""
        vehicle, _ = self.receiver
        fuel_quantity = cast(FuelInterface, vehicle).fuel_quantity_get()
        fuel_quantity -= self._fuel_expense_get()
        cast(FuelInterface, vehicle).fuel_quantity_set(fuel_quantity)


class StraightMoveWithFuelCommand(MacroCommand):
    """Перемещение по прямой с контролем и расходом топлива"""
    def __init__(self, receiver: Any):
        """:param receiver: перемещаемый объект"""
        check = CheckFuelCommand((receiver, receiver.direction_get()))
        move = StraightMoveCommand(receiver)
        burn = BurnFuelCommand((receiver, receiver.direction_get()))
        super().__init__((check, move, burn))
