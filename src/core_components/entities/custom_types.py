#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from type_protocols import *
from typing import Protocol, Tuple, runtime_checkable
import numpy as np

from core_components.maps.tiles.base import TileCoordinate

@runtime_checkable
class EntitySubState(Protocol):
    machine: Machine
    name: str
    store: StatefulObject
    state_bit_dtypes: Tuple[np.dtype, ...]


@runtime_checkable
class EntityParentState(Protocol):
    machine: Machine
    substates: list[EntitySubState]


@runtime_checkable
class GameEntity(Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None

    
# @runtime_checkable
# class MobileEntity(GameEntity, Protocol):
#     """The MobileEntity Protocol is a mixin class that has movement capabilities."""
#     speed: int | None
#     destination: TileCoordinate | None

#     def move(self):
#         ...

# @runtime_checkable
# class TargetingEntity(GameEntity, Protocol):
#     """The TargetingEntity Protocol is a mixin class that has a 'target' attribute."""
#     target: GameEntity | None

# @runtime_checkable
# class TargetableEntity(GameEntity, Protocol):
#     """The TargetableEntity Protocol is a mixin class that can be targeted by other entities."""
#     targeter: GameEntity | None

# @runtime_checkable
# class MortalEntity(GameEntity, Protocol):
#     """The MortalEntity Protocol is a mixin class that has health attributes."""
#     physical: Any | None

# @runtime_checkable
# class CombatEntity(GameEntity, Protocol):
#     """The CombatEntity Protocol is a mixin class that has combat attributes."""
#     combat: Any | None

# @runtime_checkable
# class SightedEntity(GameEntity, Protocol):
#     """The SightedEntity Protocol is a mixin class that has sight attributes."""
#     fov_radius: int | None

# @runtime_checkable
# class GameAIEntity(GameEntity, Protocol):
#     """The GameAIEntity Protocol is a mixin class that has an 'ai' attribute."""
#     ai: StateTransformer | None