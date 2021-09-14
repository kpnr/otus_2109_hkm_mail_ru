"""Запускаемый модуль"""

from lesson3.bases import DynamicInterfaceObject
from lesson3.implementations import (
    Movable, SpaceVector2, SpaceDirection, StraightMoveCommand,
    RotationCommand
    )
from pprint import pprint
from math import pi

tank = DynamicInterfaceObject()
pos = Movable(SpaceVector2(12.0, 5.0))
speed = SpaceDirection(SpaceVector2(-7.0, 3.0))
tank.absorb(pos)
tank.absorb(speed)
cmd = StraightMoveCommand(tank)
cmd.execute()
pprint([tank.position_get().__dict__, tank.direction_get().__dict__], depth=3)
cmd = RotationCommand([tank, SpaceVector2(90.0, pi/180.0)])
cmd.execute()
pprint([tank.position_get().__dict__, tank.direction_get().__dict__], depth=3)

