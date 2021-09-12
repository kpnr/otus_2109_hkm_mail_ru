"""Запускаемый модуль"""

from lesson3.bases import DynamicInterfaceObject
from lesson3.implementations import (
    Position, Movable, SpaceVector2, SpaceDirection, StraightMoveCommand
    )
from pprint import pprint

tank = DynamicInterfaceObject()
pos = Position(SpaceVector2(12, 5))
speed = SpaceDirection(SpaceVector2(-7, 3))
tank.absorb(pos)
tank.absorb(speed)
cmd = StraightMoveCommand(tank)
cmd.execute()
pprint(tank.position_get().__dict__, depth=3)
