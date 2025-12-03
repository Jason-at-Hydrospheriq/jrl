#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
   from engine import Engine
   from entities import PhysicalObject, Charactor, AICharactor


class Action(Protocol):
    
    def perform(self) -> None:
        ...


class BaseAction:

    def __init__(self, entity: PhysicalObject | Charactor | AICharactor) -> None:
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.game_map.engine

    def perform(self) -> None:
        ...  # To be implemented by subclasses.


class ActionOnTarget(BaseAction):
    def __init__(self, entity: PhysicalObject | Charactor | AICharactor, dx: int, dy: int) -> None:
        super().__init__(entity)
        
        self.target_dx = dx
        self.target_dy = dy


class ActionOnDestination(BaseAction):

    def __init__(self, entity: PhysicalObject | Charactor | AICharactor, dx: int, dy: int) -> None:
        super().__init__(entity)

        self.entity.dx = dx
        self.entity.dy = dy


class NoAction(BaseAction):
    def perform(self) -> None:
        pass


class EscapeAction(BaseAction):
    def perform(self) -> None:
        raise SystemExit()


class SystemExitAction(BaseAction):
    def perform(self) -> None:
        raise SystemExit()
    

class MoveAction(ActionOnDestination):
    def perform(self) -> None:

        if self.entity.collision: # Destination is blocked by an entity, wall, or map boundary.
            # If obstacle is an ai_actor, perform a melee attack instead.
            obstacle = self.entity.game_map.get_entity_at_location(self.entity.destination)
            if obstacle and obstacle in self.entity.game_map.live_ai_actors:
                return MeleeAction(self.entity, self.entity.dx, self.entity.dy).perform()
            
            return  # Destination is blocked by an entity, wall, or map boundary.
        
        self.entity.move(self) # type: ignore


class MeleeAction(ActionOnTarget):
    def perform(self) -> None:

        target = self.entity.game_map.get_entity_at_location(self.entity.target_location)

        if not target:
            return  # No entity to attack.

        damage = self.entity.combat.attack_power - target.combat.defense  # type: ignore
        attack_desc = f"{self.entity.name} attacks {target.name}"

        if damage > 0:
            print(f"{attack_desc} for {damage} hit points.")

            if target.physical:
                target.physical.hp -= damage
        else:
            print(f"{attack_desc} but does no damage.")
