"""Реализации интерфейсов/абстракций"""

from typing import Any, Optional, cast

from lesson13.interfaces import FuelInterface, MetricVectorInterface
from lesson3.interfaces import GenericCommand
from lesson3.implementations import SpaceVector2


class CommandException(Exception):
    """Исключение выполнения команды"""
    def __init__(self, cmd: Optional[GenericCommand]):
        self.command = cmd
        super(CommandException, self).__init__(cmd)


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


class CheckFuelCommand(GenericCommand):
    """Проверить кол-во топлива, достаточное для движения"""
    def __init__(self, vehicle: FuelInterface, movement: MetricVectorInterface):
        FuelInterface._assert_support(vehicle)
        MetricVectorInterface._assert_support(movement)
        super().__init__((vehicle, movement))

    def _fuel_expense_get(self) -> float:
        """Получить фактический расход топлива"""
        vehicle, movement = self.receiver
        length = cast(MetricVectorInterface, movement).length()
        f_rate = cast(FuelInterface, vehicle).fuel_rate_get()
        rv = f_rate * length
        return rv

    def execute(self) -> None:
        """Контроль досаточности топлива"""
        vehicle, _ = self.receiver
        f_quantity = cast(FuelInterface, vehicle).fuel_quantity_get()
        if f_quantity < self._fuel_expense_get():
            raise CommandException(self)
        # Проверка уровня топлива прошла


class BurnFuelCommand(CheckFuelCommand):
    """Израсходовать топливо"""

    def execute(self) -> None:
        """Уничтожение топлива для перехода"""
        vehicle, _ = self.receiver
        f_quantity = cast(FuelInterface, vehicle).fuel_quantity_get()
        f_quantity -= self._fuel_expense_get()
        cast(FuelInterface, vehicle).fuel_quantity_set(f_quantity)
