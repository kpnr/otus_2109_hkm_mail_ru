"""Реализации интерфейсов и базовых классов"""

from __future__ import annotations
from typing import Any, cast
from .interfaces import (UObject, GenericCommand, SpaceDirectionInterface,
                         MovableInterface, SpaceVectorInterface)
from math import sin, cos


class SpaceVector2(SpaceVectorInterface):
    """Двумерный вектор"""
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def move_by(self, other: SpaceVectorInterface) -> SpaceVectorInterface:
        """Сложение по правилу параллеограмма"""
        if not isinstance(other, self.__class__):
            raise TypeError('Can not move such vector', self, other)
        rv = SpaceVector2(self.x + other.x, self.y + other.y)
        return rv

    def rotate(self, rotation: SpaceVectorInterface) -> SpaceVectorInterface:
        """Вращение на угол rotation.x*rotation.y радиан"""
        if not isinstance(rotation, self.__class__):
            raise TypeError('Can not rotate such vector', self, rotation)
        angle = rotation.x * rotation.y
        x, y = self.x, self.y
        rv = SpaceVector2(x * cos(angle) - y * sin(angle),
                          x * sin(angle) + y * cos(angle))
        return rv


# noinspection PyMissingOrEmptyDocstring
class FixedPosition(MovableInterface):
    """Объект-позиция"""
    def __init__(self, position: SpaceVectorInterface):
        self.position = position

    def position_get(self) -> SpaceVectorInterface:
        rv = self.position
        return rv

    def position_set(self, new_pos: SpaceVectorInterface) -> None:
        raise RuntimeError("Запрещено изменение позиции объекта.")


# noinspection PyMissingOrEmptyDocstring
class Movable(MovableInterface):
    """Объект, позволяющий изменять позицию"""
    def __init__(self, position: SpaceVectorInterface):
        self.position = position

    def position_get(self) -> SpaceVectorInterface:
        rv = self.position
        return rv

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


class StraightMoveAdapter:
    """Перемещение из текущей позиции в текущем направлении"""
    def __init__(self, obj: UObject):
        MovableInterface._assert_support(obj)
        SpaceDirectionInterface._assert_support(obj)
        self.obj = obj

    def move(self) -> None:
        """Осуществить перемещение"""
        speed = cast(SpaceDirectionInterface, self.obj).direction_get()
        position = cast(MovableInterface, self.obj).position_get()
        new_position = position.move_by(speed)
        self.obj.position_set(new_position)


class RotationAdapter:
    """Вращение объекта"""
    def __init__(self, obj: UObject, rotation: SpaceVectorInterface):
        SpaceDirectionInterface._assert_support(obj)
        self.obj = cast(SpaceDirectionInterface, obj)
        self.rotation = rotation

    def rotate(self) -> None:
        """Осуществить вращение"""
        direction = self.obj.direction_get()
        new_direction = direction.rotate(self.rotation)
        self.obj.direction_set(new_direction)


class StraightMoveCommand(GenericCommand):
    """Передвижение объекта основываясь на его текущем положении и скорости"""
    def __init__(self, receiver: Any):
        """Перемещаем только объекты на поле боя"""
        adapter = StraightMoveAdapter(receiver)
        super().__init__(adapter)

    def execute(self) -> None:
        """Непосредственное перемещение объекта"""
        self.receiver.move()
        return


# noinspection PyMissingOrEmptyDocstring
class RotationCommand(GenericCommand):
    """Поворот объектов, обладающих направленностью"""
    def __init__(self, receiver: Any):
        obj, rotation = receiver
        adapter = RotationAdapter(obj, rotation)
        super().__init__(adapter)

    def execute(self) -> None:
        self.receiver.rotate()


class Tank(UObject):
    """Танк. Никаких спецсвойств (пока) не имеет"""
