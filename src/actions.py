#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Tuple, Protocol
import numpy as np

if TYPE_CHECKING:
   from engine import Engine
   from entities import Entity
   from game_map import GameMap


class Action(Protocol):
    entity: Entity

    def __init__(self, entity: Entity) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        ...  # To be implemented by subclasses.


class ActionOnTarget(Action):
    def __init__(self, entity: Entity, dx: int, dy: int) -> None:
        super().__init__(entity)
        self.dx = dx
        self.dy = dy
    
    @property
    def target_location(self) -> np.ndarray:
        entity_target = self.entity.game_map.get_entity_location(self.entity)
        entity_target['x'] += self.dx
        entity_target['y'] += self.dy

        return entity_target

    @property
    def target_entity(self) -> Optional[Entity]:
        return self.entity.game_map.get_entity_by_location(self.target_location)
    
class NoAction(Action):
    def perform(self) -> None:
        pass


class EscapeAction(Action):
    def perform(self) -> None:
        raise SystemExit()


class SystemExitAction(Action):
    def perform(self) -> None:
        raise SystemExit()
    

class MovementAction(ActionOnTarget):
    def perform(self) -> None:

        if not self.entity.game_map.in_bounds(self.target_location):
            return  # Destination is out of bounds.
        if not self.entity.game_map.tiles["walkable"][self.target_location['x'], self.target_location['y']]:
            return  # Destination is blocked by a tile.
        
        self.entity.move(self) # type: ignore


class MeleeAction(ActionOnTarget):
    def perform(self) -> None:

        if not self.target_entity:
            return  # No entity to attack.

        print(f"You kick the {self.target_entity.name}, much to its annoyance!")


class CollisionAction(ActionOnTarget):
    def perform(self) -> None:

        if self.target_entity:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()