#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
   from engine import Engine
   from entities import Entity
   from game_map import GameMap


class Action:
   def perform(self, engine: Engine, entity: Entity) -> None:
       """
       Perform this action with the objects needed to determine its scope. This method must be overridden by Action subclasses.

       Args:
              engine: The engine instance.
              entity: The entity performing the action.

        Raises:
                NotImplementedError: If the action is not implemented.
        Returns:
                None

       """
       raise NotImplementedError()


class ActionOnTarget(Action):
    def __init__(self, dx: int, dy: int) -> None:

        self.dx = dx
        self.dy = dy
    
    def get_target_location(self, game_map: GameMap, entity: Entity) -> np.ndarray:
        entity_target = game_map.get_entity_location(entity)
        entity_target['x'] += self.dx
        entity_target['y'] += self.dy

        return entity_target
    
    def perform(self, engine: Engine, entity: Entity) -> None:
        """
        Perform this action with the objects needed to determine its scope. This method must be overridden by Action subclasses.

        Args:
                engine: The engine instance.
                entity: The entity performing the action.

            Raises:
                    NotImplementedError: If the action is not implemented.
            Returns:
                    None

        """
        raise NotImplementedError()


class NoAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        pass


class EscapeAction(Action):
    def perform(self, engine: Engine, entity: Entity) -> None:
        raise SystemExit()


class MovementAction(ActionOnTarget):
    def perform(self, engine: Engine, entity: Entity) -> None:
        
        target_location = self.get_target_location(engine.game_map, entity)

        if not engine.game_map.in_bounds(target_location):
            return  # Destination is out of bounds.
        if not engine.game_map.tiles["walkable"][target_location['x'], target_location['y']]:
            return  # Destination is blocked by a tile.
        
        entity.move(self) # type: ignore


class MeleeAction(ActionOnTarget):
    def perform(self, engine: Engine, entity:Entity) -> None:
        
        target_location = self.get_target_location(engine.game_map, entity)
        target_entity = engine.game_map.get_entity_by_location(target_location)

        if not target_entity:
            return  # No entity to attack.

        print(f"You kick the {target_entity.name}, much to its annoyance!")


class CollisionAction(ActionOnTarget):
    def perform(self, engine: Engine, entity: Entity) -> None:
        target_location = self.get_target_location(engine.game_map, entity)
        target_entity = engine.game_map.get_entity_by_location(target_location)

        if not target_entity:
            return MovementAction(self.dx, self.dy).perform(engine, entity)
        else:
            return MeleeAction(self.dx, self.dy).perform(engine, entity)