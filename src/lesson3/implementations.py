"""Реализации интерфейсов и базовых классов"""

from __future__ import annotations
from typing import Any, cast
from .bases import GenericCommand
from .interfaces import (PositionedInterface, SpaceDirectionInterface,
                         MovableInterface, SpaceVectorInterface)


class SpaceVector2(SpaceVectorInterface):
    """Двумерный вектор"""
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def increase(self, other: SpaceVectorInterface) -> SpaceVectorInterface:
        """Сложение по правилу параллеограмма"""
        if not isinstance(other, self.__class__):
            raise TypeError('Can not increase such vector', self, other)
        rv = SpaceVector2(self.x + other.x, self.y + other.y)
        return rv


class StraightMoveCommand(GenericCommand):
    """Передвижение объекта основываясь на его текущем положении и скорости"""
    def __init__(self, receiver: Any):
        """Перемещаем только объекты на поле боя"""
        MovableInterface._assert_support(receiver)
        SpaceDirectionInterface._assert_support(receiver)
        super().__init__(receiver)

    def execute(self) -> None:
        """Непосредственное перемещение объекта"""
        obj = self.receiver
        position = cast(PositionedInterface, obj).position_get()
        speed = cast(SpaceDirectionInterface, obj).direction_get()
        position = position.increase(speed)
        cast(MovableInterface, obj).position_set(position)
        return


# noinspection PyMissingOrEmptyDocstring
class Position(PositionedInterface):
    """Объект-позиция"""
    def __init__(self, position: SpaceVectorInterface):
        self.position = position

    def position_get(self) -> SpaceVectorInterface:
        rv = self.position
        return rv


# noinspection PyMissingOrEmptyDocstring
class Movable(Position, MovableInterface):
    """Объект, позволяющий изменять позицию"""
    def position_set(self, new_pos: SpaceVectorInterface) -> None:
        self.position = new_pos
        return


# noinspection PyMissingOrEmptyDocstring
class SpaceDirection(SpaceDirectionInterface):
    """Объект с направлением в пространстве"""
    def __init__(self, direction: SpaceVectorInterface):
        self.direction = direction

    def direction_get(self) -> SpaceVectorInterface :
        rv = self.direction
        return rv

    def direction_set(self, new_dir: SpaceVectorInterface) -> None :
        self.direction = new_dir
        return
