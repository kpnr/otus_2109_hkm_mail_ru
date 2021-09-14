"""Тесты для Урока №3"""

import pytest

from lesson3.implementations import (
    Tank, Position,Movable, SpaceVector2, SpaceDirection, StraightMoveCommand,
    RotationCommand
    )
from math import pi


def create_objects():
    rv = (
        Tank(),
        Movable(SpaceVector2(12.0, 5.0)),
        SpaceDirection(SpaceVector2(-7.0, 3.0)),
        SpaceVector2(90, pi/180)
    )
    return rv


def test_move_by():
    tank, pos, speed, _ = create_objects()
    tank.absorb(pos).absorb(speed)

    move_command = StraightMoveCommand(tank)
    move_command.execute()

    pos = tank.position_get()
    assert (pos.x == pytest.approx(5.0))
    assert (pos.y == pytest.approx(8.0))


def test_not_positioned():
    tank, _, speed, _ = create_objects()
    tank.absorb(speed)

    with pytest.raises(AttributeError):
        move_command = StraightMoveCommand(tank)
        move_command.execute()


def test_not_directed():
    tank, pos, _, _ = create_objects()
    tank.absorb(pos)

    with pytest.raises(AttributeError):
        move_command = StraightMoveCommand(tank)
        move_command.execute()


def test_fixed_pos():
    tank, _, speed, _ = create_objects()
    pos = Position(SpaceVector2(12.0, 5.0))
    tank.absorb(pos).absorb(speed)

    with pytest.raises(AttributeError):
        move_command = StraightMoveCommand(tank)
        move_command.execute()


def test_rotate():
    tank, pos, speed, rot = create_objects()
    tank.absorb(pos).absorb(speed)

    rot_command = RotationCommand([tank, rot])
    rot_command.execute()

    speed = tank.direction_get()
    assert (speed.x == pytest.approx(-3.0))
    assert (speed.y == pytest.approx(-7.0))
